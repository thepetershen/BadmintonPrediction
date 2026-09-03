import joblib
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import pandas as pd
from src.match.rank_lookup import get_rank
import os

app = FastAPI()

# set some default allowed originings
_DEFAULT_ORIGINS = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

allowed_origins = [
  origin.strip()
  for origin in os.environ.get("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
  if origin.strip()
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_methods=["*"],
  allow_headers=["*"],
)
# this is the best model we have trained in terms of testing accuracy
model = joblib.load('data/models/xgb_badminton_model.joblib')

# so the challenge of this endpoint, is that the user can only give us the names of the 
# players they want us to scrape. we need to be able to find out using their name, their rank, and also there head to head
# the head to head can easily be found.

# load the name to id

with open('data/name_to_id.json', 'r') as f:
  name_to_id = {str(k): v for k, v in json.load(f).items()}

with open('data/ms_name_to_id.json', 'r') as f:
  ms_name_to_id = {str(k): v for k, v in json.load(f).items()}

with open('data/ws_name_to_id.json', 'r') as f:
  ws_name_to_id = {str(k): v for k, v in json.load(f).items()}

with open('data/h2h.json', 'r') as f:
  h2h = {str(k): v for k, v in json.load(f).items()}

ms_player_list = []
for key, value in ms_name_to_id.items():
  ms_player_list.append(key)
ms_player_list.sort()

ws_player_list = []
for key, value in ws_name_to_id.items():
  ws_player_list.append(key)
ws_player_list.sort()



# headers for getting ranks
headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'origin': 'https://bwfbadminton.com',
  'priority': 'u=1, i',
  'referer': 'https://bwfbadminton.com/',
  'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
}

params = {
  'playerId': '57945',
  'rankingId': '2',
  'rankingCategoryId': '6',
  'year': '2024',
  'week': '2',
}

@app.get("/players/{category}")
def list_players(category: str):
  if category == "MS":
    return ms_player_list
  elif category == "WS":
    return ws_player_list
  else: 
    raise HTTPException(status_code=404, detail="invalid category")

@app.get("/predict/matchup/{player1_name}/{player2_name}")
def predict_match(player1_name: str, player2_name: str):

  player1_id = name_to_id.get(player1_name)
  player2_id = name_to_id.get(player2_name)

  if player1_id is None or player2_id is None:
    raise HTTPException(status_code=404, detail="Could not find one or both players")

  h2h_tuple = tuple(sorted((player1_id, player2_id)))
  h2h_key = h2h_tuple[0] + "_" + h2h_tuple[1]
  h2h_row = h2h.get(h2h_key)

  if (h2h_row == None):
    h2h_win_rate = 0.5
  else:
    player1_win = h2h_row.get(player1_id)
    player2_win = h2h_row.get(player2_id)
    total_win = player1_win + player2_win
    h2h_win_rate = player1_win / total_win

  today = date.today()
  #allow for a 2 week drag (it could be the case that)
  week_number = today.isocalendar()[1] - 2 if today.isocalendar()[1] >= 2 else 0
  year = today.isocalendar().year


  #when a player enters name, we will just assume its the lastest
  player1_rank, player1_highest_rank = get_rank(player1_id, year, week_number, params=params, headers=headers)
  player2_rank, player2_highest_rank = get_rank(player2_id, year, week_number, params=params, headers=headers)

  # if a player has no current ranking data, assume they're bad and fall back to a worst-case rank
  UNRANKED_FALLBACK = 300
  player1_rank = player1_rank if player1_rank is not None else UNRANKED_FALLBACK
  player1_highest_rank = player1_highest_rank if player1_highest_rank is not None else UNRANKED_FALLBACK
  player2_rank = player2_rank if player2_rank is not None else UNRANKED_FALLBACK
  player2_highest_rank = player2_highest_rank if player2_highest_rank is not None else UNRANKED_FALLBACK

  rank_diff = int(player1_rank) - int(player2_rank)
  rank_highest_diff = int(player1_highest_rank) - int(player2_highest_rank)

  # the model has no structural guarantee that f(-x) == 1 - f(x), so predicting player1
  # vs player2 could disagree with predicting player2 vs player1. we score by making it symmetric by adding the inverse. 
  X = pd.DataFrame([
    {
      "h2h_win_rate": h2h_win_rate,
      "rank_diff": rank_diff,
      "highest_rank_diff": rank_highest_diff,
    },
    {
      "h2h_win_rate": 1 - h2h_win_rate,
      "rank_diff": -rank_diff,
      "highest_rank_diff": -rank_highest_diff,
    },
  ])
  proba = model.predict_proba(X)   # row 0 = forward (p1,p2), row 1 = reversed (p2,p1)
  forward_p1_win_prob = float(proba[0][1])
  reversed_p1_win_prob = float(proba[1][1])

  p1_win_prob = 0.5 + (forward_p1_win_prob - reversed_p1_win_prob) / 2

  # we simply return the probability player 1 wins
  return {"player1_name": player1_name, "player2_name": player2_name, "prediction": p1_win_prob }


