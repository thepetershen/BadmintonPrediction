import pandas as pd

# the goal of this file is to process the the file to add extra features name rank diff, head to head, and an elo calculation in order to
# add features into tabular ML model

# we will use a dictionary to keep track of player elo and h2h
# the h2h will only be calculated with the data we have. 

# takes in the elos, the winner, and returns the new elos
def update_elo(elo_1, elo_2, winner, k=32):
    expected_1 = 1 / (1 + 10 ** ((elo_2 - elo_1) / 400))
    expected_2 = 1 - expected_1  # expected_2 is simply the inverse of expected_1

    score_1 = 1 if winner == 1 else 0
    score_2 = 1 - score_1

    new_elo_1 = elo_1 + (k * (score_1 - expected_1))
    new_elo_2 = elo_2 + (k * (score_2 - expected_2))

    return new_elo_1, new_elo_2

def add_features():
  df = pd.read_csv("data/all_match_id.csv", parse_dates=["match_date"])
  # we will assume the df is sorted by date already (it should be as we aded in order)
  player_elo = {}       # player_id -> current Elo rating
  h2h_tracker = {}      # (player_1_id, player_2_id) -> [p1_wins, p2_wins]

  new_features = {
    "p1_elo_pre_match": [],
    "p2_elo_pre_match": [],
    "h2h_win_rate": [],
    "rank_diff": [],
    "highest_rank_diff": []
  }

  for row, index in df.iterrows():
    p1_id = row["player_1_id"]
    p2_id = row["player_2_id"]
    winner_id = row["winner_id"]

    #default elo is 1500
    p1_current_elo = player_elo.get(p1_id, 1500)
    p2_current_elo = player_elo.get(p2_id, 1500)

    rank_diff = row["player_1_rank"] - row["player_2_rank"]
    highest_rank_diff = row["player_1_rank_highest"] - row["player_1_rank_highest"]

    h2h = h2h_tracker.get((p1_id, p2_id), [0, 0])
    if (winner_id == p2_id):
      h2h[1] += 1
    else:
      h2h[0] += 1

    
    



