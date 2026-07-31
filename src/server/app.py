import joblib

from fastapi import FastAPI

app = FastAPI()
# this is the best model we have trained in terms of testing accuracy
model = joblib.load('data/models/xgb_badminton_model.joblib')

# so the challenge of this endpoint, is that the user can only give us the names of the 
# players they want us to scrape. we need to be able to find out using their name, their rank, and also there head to head
# the head to head can easily be found.


app.get("/")
def predict_winner():
  return 


