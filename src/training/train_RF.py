
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

def split_data():
  df = pd.read_csv("data/all_match_id_proccessed.csv")

  df['match_date'] = pd.to_datetime(df['match_date'])
  df['p1_won'] = (df['winner_id'] == df['player_1_id']).astype(int) # its just conventient to put this code here
  # we will split into train, validation, and testing
  train_df = df[df['match_date'] < '2025-08-01']

  val_df = df[(df['match_date'] >= '2025-08-01') & (df['match_date'] < '2026-01-01')]

  test_df = df[df['match_date'] >= '2026-01-01']

  print(len(train_df), len(val_df), len(test_df))

  return train_df, val_df, test_df
# this function will do things like dropping all the features that can't be and shouldn't be put into a random forest 
# model and will make it into x train y trian and other forms of data that can be fed direclty into the model
def prepare_data(train_df, val_df, test_df):

  columns_to_drop = ["tournament_name", "tournament_level", "match_date", "round_name", "player_1_id", "player_2_id", "winner_id",
                     "g1_p1_score", "g1_p2_score", "g2_p1_score", "g2_p2_score", "g3_p1_score", "g3_p2_score"]
                
  target_col = "p1_won"

  def to_x_y(df):
    df = df.drop(columns=columns_to_drop)
    df = df.dropna()
    x = df.drop(columns=[target_col])
    y = df[target_col]
    return x, y

  x_train, y_train = to_x_y(train_df)
  x_val, y_val = to_x_y(val_df)
  x_test, y_test = to_x_y(test_df)

  return x_train, y_train, x_val, y_val, x_test, y_test

def train(x_train, y_train, x_val, y_val, x_test, y_test):
  rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

  rf_model.fit(x_train, y_train)

  y_val_pred = rf_model.predict(x_val)

  accuracy = accuracy_score(y_val, y_val_pred)
  print(f"RF Accuracy: {accuracy * 100:.2f}%\n")
  print(classification_report(y_val, y_val_pred))



def train_RF():
  train_df, val_df, test_df = split_data()
  x_train, y_train, x_val, y_val, x_test, y_test = prepare_data(train_df, val_df, test_df)

  train(x_train, y_train, x_val, y_val, x_test, y_test)


if __name__ == "__main__":
  train_RF()