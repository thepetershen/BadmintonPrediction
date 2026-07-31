import joblib
import json
from fastapi import FastAPI

app = FastAPI()
# this is the best model we have trained in terms of testing accuracy
model = joblib.load('data/models/xgb_badminton_model.joblib')

# so the challenge of this endpoint, is that the user can only give us the names of the 
# players they want us to scrape. we need to be able to find out using their name, their rank, and also there head to head
# the head to head can easily be found.

# load the name to id
with open('data/name_to_id.json', 'r') as f:
  name_to_id = {str(k): v for k, v in json.load(f).items()}

with open('data/h2h.json', 'r') as f:
  h2h = {str(k): v for k, v in json.load(f).items()}


@app.get("/predict/matchup/{player1_id}/{player2_id}")
def predict_match(player1_id: int, player2_id: int):
    
  return {"player1_id": player1_id, "player2_id": player2_id, "prediction": ...}


