import pandas as pd
import json

# a player only ever competes in one category (MS or WS), so we can split the
# name id lookup in two just by reading match category
def split_ms_ws_names():
  df_name = pd.read_csv("data/all_match_name.csv")
  df_id = pd.read_csv("data/all_match_id.csv")

  ms_name_to_id = {}
  ws_name_to_id = {}

  for index in range(0, len(df_name)):
    df_name_row = df_name.iloc[index]
    df_id_row = df_id.iloc[index]

    category = df_name_row["match_category"]
    target = ms_name_to_id if category == "MS" else ws_name_to_id

    target[df_name_row["player_1_name"]] = str(df_id_row["player_1_id"])
    target[df_name_row["player_2_name"]] = str(df_id_row["player_2_id"])

  with open("data/ms_name_to_id.json", 'w') as f:
    json.dump(ms_name_to_id, f, indent=4)

  with open("data/ws_name_to_id.json", 'w') as f:
    json.dump(ws_name_to_id, f, indent=4)

  return ms_name_to_id, ws_name_to_id


if __name__ == "__main__":
  ms_name_to_id, ws_name_to_id = split_ms_ws_names()
  print(f"MS players: {len(ms_name_to_id)}")
  print(f"WS players: {len(ws_name_to_id)}")
