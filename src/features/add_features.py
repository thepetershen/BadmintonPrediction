import pandas as pd

# the goal of this file is to process the the file to add extra features name rank diff, head to head, and an elo calculation in order to
# add features into tabular ML model

# we will use a dictionary to keep track of player elo and h2h
# the h2h will only be calculated with the data we have. 

# takes in the elos and player 1's score for the match (1 for a win, 0 for a loss,
# or a continuous value like point share for a margin-based elo), returns the new elos
def update_elo(elo_1, elo_2, score_1, k=32):
    expected_1 = 1 / (1 + 10 ** ((elo_2 - elo_1) / 400))
    expected_2 = 1 - expected_1  # expected_2 is simply the inverse of expected_1

    score_2 = 1 - score_1

    new_elo_1 = elo_1 + (k * (score_1 - expected_1))
    new_elo_2 = elo_2 + (k * (score_2 - expected_2))

    return new_elo_1, new_elo_2

# sums the points won by each player across all games played in the match
def get_match_points(row):
    p1_points = 0
    p2_points = 0
    for game in ["g1", "g2", "g3"]:
        p1_score = row[f"{game}_p1_score"]
        p2_score = row[f"{game}_p2_score"]
        if pd.notna(p1_score) and pd.notna(p2_score):
            p1_points += p1_score
            p2_points += p2_score
    return p1_points, p2_points

def add_features():
  df = pd.read_csv("data/all_match_id.csv", parse_dates=["match_date"])
  # we will assume the df is sorted by date already (it should be as we aded in order)
  player_elo = {}       # player_id -> current Elo rating
  player_point_elo = {} # player_id -> current point-share Elo rating
  h2h_tracker = {}      # (player_1_id, player_2_id) -> [p1_wins, p2_wins]

  h2h_correct = 0   # predictions made using prior h2h record that were right
  h2h_total = 0      # matches where the two players had a prior head-to-head record

  new_features = {
    "p1_elo_pre_match": [],
    "p2_elo_pre_match": [],
    "p1_point_elo_pre_match": [],
    "p2_point_elo_pre_match": [],
    "h2h_win_rate": [],
    "rank_diff": [],
    "highest_rank_diff": []
  }

  for index, row in df.iterrows():
    p1_id = row["player_1_id"]
    p2_id = row["player_2_id"]
    winner_id = row["winner_id"]

    #default elo is 1500
    p1_current_elo = player_elo.get(p1_id, 1500)
    p2_current_elo = player_elo.get(p2_id, 1500)
    p1_current_point_elo = player_point_elo.get(p1_id, 1500)
    p2_current_point_elo = player_point_elo.get(p2_id, 1500)

    rank_diff = row["player_1_rank"] - row["player_2_rank"]
    highest_rank_diff = row["player_1_rank_highest"] - row["player_2_rank_highest"]

    h2h = h2h_tracker.get((p1_id, p2_id), [0, 0])
    total_h2h = h2h[0] + h2h[1]
    h2h_win_rate = h2h[0] / total_h2h if total_h2h > 0 else 0.5

    if h2h[0] != h2h[1]:
      h2h_prediction = p1_id if h2h[0] > h2h[1] else p2_id
      h2h_total += 1
      if h2h_prediction == winner_id:
        h2h_correct += 1

    new_features["p1_elo_pre_match"].append(p1_current_elo)
    new_features["p2_elo_pre_match"].append(p2_current_elo)
    new_features["p1_point_elo_pre_match"].append(p1_current_point_elo)
    new_features["p2_point_elo_pre_match"].append(p2_current_point_elo)
    new_features["h2h_win_rate"].append(h2h_win_rate)
    new_features["rank_diff"].append(rank_diff)
    new_features["highest_rank_diff"].append(highest_rank_diff)

    if (winner_id == p2_id):
      h2h[1] += 1
    else:
      h2h[0] += 1
    h2h_tracker[(p1_id, p2_id)] = h2h

    new_p1_elo, new_p2_elo = update_elo(p1_current_elo, p2_current_elo, 1.0 if winner_id == p1_id else 0.0)
    player_elo[p1_id] = new_p1_elo
    player_elo[p2_id] = new_p2_elo

    p1_points, p2_points = get_match_points(row)
    total_points = p1_points + p2_points
    point_share_1 = p1_points / total_points if total_points > 0 else 0.5

    new_p1_point_elo, new_p2_point_elo = update_elo(p1_current_point_elo, p2_current_point_elo, point_share_1)
    player_point_elo[p1_id] = new_p1_point_elo
    player_point_elo[p2_id] = new_p2_point_elo

  for col_name, col_data in new_features.items():
    df[col_name] = col_data

  h2h_accuracy = h2h_correct / h2h_total if h2h_total > 0 else 0.0
  print(f"Head-to-head baseline accuracy: {h2h_accuracy * 100:.2f}% ({h2h_correct}/{h2h_total} matches with a prior h2h record)")

  df.to_csv("data/all_match_id_proccessed.csv", index=False)

  return df

if __name__ == "__main__":
  add_features()
