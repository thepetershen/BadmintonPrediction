
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib

from src.training.date_splits import split_by_date

def split_data():
  df = pd.read_csv("data/all_match_id_proccessed.csv")

  df['match_date'] = pd.to_datetime(df['match_date'])
  df['p1_won'] = (df['winner_id'] == df['player_1_id']).astype(int) # its just conventient to put this code here
  # we will split into train, validation, and testing
  train_df, val_df, test_df = split_by_date(df)

  print(len(train_df), len(val_df), len(test_df))

  return train_df, val_df, test_df

def mirror_x_y(x, y):
  # order-swapped counterpart of each row. negating each element so there is no error for flips. 
  # this method simply mirrors the data and adds it to training.
  x_mirror = x.copy()
  x_mirror["rank_diff"] = -x_mirror["rank_diff"]
  x_mirror["highest_rank_diff"] = -x_mirror["highest_rank_diff"]
  x_mirror["h2h_win_rate"] = 1 - x_mirror["h2h_win_rate"]
  y_mirror = 1 - y

  x_aug = pd.concat([x, x_mirror], ignore_index=True)
  y_aug = pd.concat([y, y_mirror], ignore_index=True)
  return x_aug, y_aug

# this function will do things like dropping all the features that can't be and shouldn't be put into a random forest 
# model and will make it into x train y trian and other forms of data that can be fed direclty into the model
def prepare_data(train_df, val_df, test_df, augment=True):

  columns_to_drop = ["tournament_name", "tournament_level", "match_date", "round_name", "player_1_id", "player_2_id", "winner_id",
                     "g1_p1_score", "g1_p2_score", "g2_p1_score", "g2_p2_score", "g3_p1_score", "g3_p2_score",
                     # raw ranks are redundant with rank_diff/highest_rank_diff (which encode the same info more directly for tree splits)
                     "player_1_rank", "player_2_rank", "player_1_rank_highest", "player_2_rank_highest",
                     # experiment: permutation importance showed these near-zero/negative on validation despite high split importance
                     "p1_elo_pre_match", "p2_elo_pre_match", "p1_point_elo_pre_match", "p2_point_elo_pre_match", "match_category"]
  target_col = "p1_won"

  def to_x_y(df):
    df = df.drop(columns=columns_to_drop)
    df = df.dropna()
    x = df.drop(columns=[target_col])
    y = df[target_col]
    if augment:
      x, y = mirror_x_y(x, y)
    return x, y

  x_train, y_train = to_x_y(train_df)
  x_val, y_val = to_x_y(val_df)
  x_test, y_test = to_x_y(test_df)

  return x_train, y_train, x_val, y_val, x_test, y_test


def train_xgb(x_train, y_train, x_val, y_val, x_test, y_test):
  xgb_model = XGBClassifier(
    n_estimators=1000,
    learning_rate=0.03,
    max_depth=4,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.5,   # L1
    reg_lambda=1.0,  # L2
    eval_metric="logloss",
    early_stopping_rounds=50,
    random_state=42,
    n_jobs=-1,
  )

  xgb_model.fit(
    x_train, y_train,
    eval_set=[(x_val, y_val)],
    verbose=False,
  )

  print(f"Best iteration: {xgb_model.best_iteration} (of {xgb_model.get_params()['n_estimators']} max)\n")

  # predict() uses auto stopping 
  y_val_pred = xgb_model.predict(x_val)

  accuracy = accuracy_score(y_val, y_val_pred)
  print(f"XGBoost Validation Accuracy: {accuracy * 100:.2f}%\n")
  print(classification_report(y_val, y_val_pred))

  importances = pd.Series(xgb_model.feature_importances_, index=x_train.columns).sort_values(ascending=False)
  print("Feature importances (split-based):")
  print(importances)

  perm_result = permutation_importance(xgb_model, x_val, y_val, n_repeats=30, random_state=42, n_jobs=-1)
  perm_importances = pd.Series(perm_result.importances_mean, index=x_val.columns).sort_values(ascending=False)
  print("\nFeature importances (permutation, on validation set):")
  print(perm_importances)
  return xgb_model


def preprocess():
  train_df, val_df, test_df = split_data()
  x_train, y_train, x_val, y_val, x_test, y_test = prepare_data(train_df, val_df, test_df)

  return x_train, y_train, x_val, y_val, x_test, y_test

def train():
  x_train, y_train, x_val, y_val, x_test, y_test = preprocess()

  model = train_xgb(x_train, y_train, x_val, y_val, x_test, y_test)

  joblib.dump(model, 'data/models/xgb_badminton_model.joblib')

if __name__ == "__main__":
  train()