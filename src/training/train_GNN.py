import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch_geometric.data import Data
from sklearn.metrics import accuracy_score, classification_report
import joblib

# this model was created by an llm as a test a GNN model. 

DATA_PATH = "data/all_match_id_proccessed.csv"
VAL_START = pd.Timestamp("2025-08-01")
TEST_START = pd.Timestamp("2026-01-01")

P1_NODE_COLS = ["p1_elo_pre_match", "p1_point_elo_pre_match", "player_1_rank"]
P2_NODE_COLS = ["p2_elo_pre_match", "p2_point_elo_pre_match", "player_2_rank"]
NODE_FEATURE_NAMES = ["elo", "point_elo", "rank"]


def load_matches():
  df = pd.read_csv(DATA_PATH, parse_dates=["match_date"])
  df = df.sort_values("match_date").reset_index(drop=True)
  df["p1_won"] = (df["winner_id"] == df["player_1_id"]).astype(int)

  # point differential, same score columns add_features.py sums per match
  game_cols = [("g1_p1_score", "g1_p2_score"), ("g2_p1_score", "g2_p2_score"), ("g3_p1_score", "g3_p2_score")]
  p1_points = sum(df[c1].fillna(0) for c1, _ in game_cols)
  p2_points = sum(df[c2].fillna(0) for _, c2 in game_cols)
  df["point_diff"] = p1_points - p2_points  # positive => player_1 won by more points

  required = ["player_1_id", "player_2_id", "winner_id"] + P1_NODE_COLS + P2_NODE_COLS
  df = df.dropna(subset=required).reset_index(drop=True)
  return df


def build_player_feature_timeline(df):
  p1_rows = df[["match_date", "player_1_id"] + P1_NODE_COLS].rename(
    columns={"player_1_id": "player_id", **dict(zip(P1_NODE_COLS, NODE_FEATURE_NAMES))})
  p2_rows = df[["match_date", "player_2_id"] + P2_NODE_COLS].rename(
    columns={"player_2_id": "player_id", **dict(zip(P2_NODE_COLS, NODE_FEATURE_NAMES))})
  timeline = pd.concat([p1_rows, p2_rows], ignore_index=True)
  return timeline.sort_values("match_date").reset_index(drop=True)


def snapshot_node_features(timeline, all_player_ids, cutoff_date):
  #Each player's most recent known feature row strictly before cutoff_date.
  #Players with no prior match get a neutral default (unrated) row.
  past = timeline[timeline["match_date"] < cutoff_date]
  default = np.array([1500.0, 1500.0, past["rank"].max() if len(past) else 300.0])

  if len(past) == 0:
    return np.tile(default, (len(all_player_ids), 1))

  latest = past.groupby("player_id")[NODE_FEATURE_NAMES].last()
  return np.stack([
    latest.loc[pid].values if pid in latest.index else default
    for pid in all_player_ids
  ]).astype(np.float32)


def build_snapshots(df):
  """
  Group matches by unique match_date. For each date's chunk of matches:
    - the graph is built ONLY from matches with match_date < this date (strict
      inequality, so same-day matches never see each other either)
    - node features are each player's latest known stats as of that same cutoff
    - the chunk itself is the supervised (p1_idx, p2_idx, y) prediction target
  This is the temporal masking: every snapshot's graph and features are a
  function of the cutoff date alone, so training on a snapshot can never leak
  information from that snapshot's own matches or anything later.
  """
  all_player_ids = pd.unique(df[["player_1_id", "player_2_id"]].values.ravel())
  id_to_idx = {pid: i for i, pid in enumerate(all_player_ids)}
  timeline = build_player_feature_timeline(df)

  snapshots = []
  for cutoff_date, chunk in df.groupby("match_date", sort=True):
    past = df[df["match_date"] < cutoff_date]

    if len(past) > 0:
      loser_id = np.where(past["p1_won"] == 1, past["player_2_id"], past["player_1_id"])
      winner_id = np.where(past["p1_won"] == 1, past["player_1_id"], past["player_2_id"])
      edge_index = torch.tensor(
        [[id_to_idx[l] for l in loser_id], [id_to_idx[w] for w in winner_id]], dtype=torch.long
      )
      point_diff = np.where(past["p1_won"] == 1, past["point_diff"], -past["point_diff"])
      days_since = (cutoff_date - past["match_date"]).dt.days.values.astype(np.float32)
      edge_attr = torch.tensor(np.stack([point_diff, days_since], axis=1), dtype=torch.float)
    else:
      edge_index = torch.empty((2, 0), dtype=torch.long)
      edge_attr = torch.empty((0, 2), dtype=torch.float)

    x = torch.tensor(snapshot_node_features(timeline, all_player_ids, cutoff_date), dtype=torch.float)

    p1_idx = torch.tensor([id_to_idx[p] for p in chunk["player_1_id"]], dtype=torch.long)
    p2_idx = torch.tensor([id_to_idx[p] for p in chunk["player_2_id"]], dtype=torch.long)
    y = torch.tensor(chunk["p1_won"].values, dtype=torch.float)

    data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
    snapshots.append((cutoff_date, data, p1_idx, p2_idx, y))

  return snapshots, len(all_player_ids)


# ---------------------------------------------------------------------------
# Model: GAT encoder + MLP decoder.
#
# A plain GCN layer aggregates neighbors as
#   h_i' = sigma( sum_{j in N(i)} (1/sqrt(deg(i) deg(j))) * W h_j )
# every neighbor's contribution is fixed by graph degree alone - beating a
# top-5 player and beating an unranked qualifier contribute identically.
#
# GAT instead learns a per-edge attention weight
#   alpha_ij = softmax_j( LeakyReLU( a^T [W h_i || W h_j || W_e e_ij] ) )
#   h_i' = sigma( sum_j alpha_ij * W h_j )
# so the model can learn that wins over strong opponents should dominate a
# player's embedding, and - because edge_attr (point_diff, days_since) feeds
# directly into the attention score - it can also learn to discount old or
# narrow wins relative to recent, decisive ones. Neither of those is
# expressible in a plain GCN. GraphSAGE is worth it if the graph is huge and
# neighbor sampling for scalability matters; with a few hundred players that
# isn't the bottleneck here, so GAT's attention is the more useful trade.
#
# The principled next step beyond this is a Temporal Graph Network (TGN):
# instead of discretizing time into per-date snapshots, TGN keeps a per-node
# memory (GRU-updated on every match) plus a continuous time encoding, so it
# never needs a snapshot granularity trade-off. Worth reaching for if this
# snapshot approach's date-bucketing turns out to lose too much recency
# signal, but it's a materially heavier build - start here first.
# ---------------------------------------------------------------------------
class MatchGNN(nn.Module):
  def __init__(self, in_channels, hidden_channels=32, num_layers=2, heads=4, edge_dim=2):
    super().__init__()
    self.convs = nn.ModuleList()
    self.convs.append(GATConv(in_channels, hidden_channels, heads=heads, concat=False, edge_dim=edge_dim))
    for _ in range(num_layers - 1):
      self.convs.append(GATConv(hidden_channels, hidden_channels, heads=heads, concat=False, edge_dim=edge_dim))

    self.decoder = nn.Sequential(
      nn.Linear(hidden_channels * 2, hidden_channels),
      nn.ReLU(),
      nn.Linear(hidden_channels, 1),
    )

  def encode(self, x, edge_index, edge_attr):
    h = x
    for conv in self.convs:
      h = F.relu(conv(h, edge_index, edge_attr=edge_attr))
    return h

  def forward(self, x, edge_index, edge_attr, p1_idx, p2_idx):
    h = self.encode(x, edge_index, edge_attr)
    pair = torch.cat([h[p1_idx], h[p2_idx]], dim=1)
    return self.decoder(pair).squeeze(-1)  # logits


def run_epoch(model, snapshots, optimizer=None, loss_fn=None):
  training = optimizer is not None
  model.train(training)

  all_logits, all_y = [], []
  total_loss, total_n = 0.0, 0
  for _, data, p1_idx, p2_idx, y in snapshots:
    if training:
      optimizer.zero_grad()

    with torch.set_grad_enabled(training):
      logits = model(data.x, data.edge_index, data.edge_attr, p1_idx, p2_idx)
      loss = loss_fn(logits, y)

    if training:
      loss.backward()
      optimizer.step()

    total_loss += loss.item() * len(y)
    total_n += len(y)
    all_logits.append(logits.detach())
    all_y.append(y)

  preds = (torch.sigmoid(torch.cat(all_logits)) > 0.5).float().numpy()
  ys = torch.cat(all_y).numpy()
  return total_loss / total_n, accuracy_score(ys, preds), preds, ys


def train_gnn(epochs=30, hidden_channels=32, num_layers=2, lr=1e-3, weight_decay=1e-4):
  df = load_matches()
  print(f"Loaded {len(df)} matches spanning {df['match_date'].min().date()} to {df['match_date'].max().date()}")

  snapshots, num_players = build_snapshots(df)
  print(f"Built {len(snapshots)} chronological snapshots across {num_players} players")

  train_snapshots = [s for s in snapshots if s[0] < VAL_START]
  val_snapshots = [s for s in snapshots if VAL_START <= s[0] < TEST_START]
  test_snapshots = [s for s in snapshots if s[0] >= TEST_START]
  print(f"{sum(len(s[4]) for s in train_snapshots)} train / "
        f"{sum(len(s[4]) for s in val_snapshots)} val / "
        f"{sum(len(s[4]) for s in test_snapshots)} test matches\n")

  in_channels = len(NODE_FEATURE_NAMES)
  model = MatchGNN(in_channels=in_channels, hidden_channels=hidden_channels, num_layers=num_layers)
  optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
  loss_fn = nn.BCEWithLogitsLoss()

  for epoch in range(1, epochs + 1):
    train_loss, train_acc, _, _ = run_epoch(model, train_snapshots, optimizer, loss_fn)
    val_loss, val_acc, _, _ = run_epoch(model, val_snapshots, optimizer=None, loss_fn=loss_fn)
    print(f"Epoch {epoch:02d}: train_loss={train_loss:.4f} train_acc={train_acc*100:.2f}%  "
          f"val_loss={val_loss:.4f} val_acc={val_acc*100:.2f}%")

  _, val_acc, val_preds, val_ys = run_epoch(model, val_snapshots, optimizer=None, loss_fn=loss_fn)
  print(f"\nFinal GNN Validation Accuracy: {val_acc * 100:.2f}%\n")
  print(classification_report(val_ys, val_preds))

  joblib.dump(model, 'data/models/gnn_badminton_model.joblib')

  return model


if __name__ == "__main__":
  train_gnn()
