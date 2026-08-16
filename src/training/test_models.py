import sys

import joblib
import numpy as np
import torch.nn as nn
from sklearn.metrics import accuracy_score, classification_report

from src.training.train_RF import split_data as rf_split_data, prepare_data as rf_prepare_data
from src.training.train_XGB import split_data as xgb_split_data, prepare_data as xgb_prepare_data
from src.training.train_GNN import load_matches, build_snapshots, run_epoch, TEST_START, MatchGNN

RF_MODEL_PATH = "data/models/rf_badminton_model.joblib"
XGB_MODEL_PATH = "data/models/xgb_badminton_model.joblib"
GNN_MODEL_PATH = "data/models/gnn_badminton_model.joblib"


def test_rf():
  model = joblib.load(RF_MODEL_PATH)
  train_df, val_df, test_df = rf_split_data()
  _, _, _, _, x_test, y_test = rf_prepare_data(train_df, val_df, test_df)

  preds = model.predict(x_test)
  acc = accuracy_score(y_test, preds)
  print(f"RF Test Accuracy: {acc * 100:.2f}%\n")
  print(classification_report(y_test, preds))
  return acc


def test_xgb(augment=True):
  model = joblib.load(XGB_MODEL_PATH)
  train_df, val_df, test_df = xgb_split_data()
  _, _, _, _, x_test, y_test = xgb_prepare_data(train_df, val_df, test_df, augment=augment)

  preds = model.predict(x_test)
  acc = accuracy_score(y_test, preds)
  print(f"XGBoost Test Accuracy (augment={augment}): {acc * 100:.2f}%\n")
  print(classification_report(y_test, preds))
  return acc


def test_gnn():
  sys.modules["__main__"].MatchGNN = MatchGNN
  model = joblib.load(GNN_MODEL_PATH)
  df = load_matches()
  snapshots, _ = build_snapshots(df)
  test_snapshots = [s for s in snapshots if s[0] >= TEST_START]

  loss_fn = nn.BCEWithLogitsLoss()
  _, acc, preds, ys = run_epoch(model, test_snapshots, optimizer=None, loss_fn=loss_fn)
  print(f"GNN Test Accuracy: {acc * 100:.2f}%\n")
  print(classification_report(ys, preds))
  return acc


def test_all():
  results = {
    "Random Forest": test_rf(),
    "XGBoost": test_xgb(),
    "GNN": test_gnn(),
  }

  print("\n=== Test Accuracy Summary ===")
  for name, acc in results.items():
    print(f"{name:15s}: {acc * 100:.2f}%")

  return results


if __name__ == "__main__":
  test_all()