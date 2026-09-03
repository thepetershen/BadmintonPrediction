import pandas as pd

VAL_START = pd.Timestamp("2026-01-01")
TEST_START = pd.Timestamp("2026-04-01")

def split_by_date(df, date_col="match_date"):
  train_df = df[df[date_col] < VAL_START]
  val_df = df[(df[date_col] >= VAL_START) & (df[date_col] < TEST_START)]
  test_df = df[df[date_col] >= TEST_START]
  return train_df, val_df, test_df
