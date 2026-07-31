import pandas as pd
import json

df_name = pd.read_csv("data/all_match_name.csv")
df_id = pd.read_csv("data/all_match_id.csv")

name_to_id = {}

for index in range(0, len(df_name)):
  df_name_row = df_name.iloc[index]
  df_id_row = df_id.iloc[index]

  name1 = df_name_row["player_1_name"]
  name2 = df_name_row["player_2_name"]

  id1 = df_id_row["player_1_id"]
  id2 = df_id_row["player_2_id"]

  name_to_id[name1] = str(id1)
  name_to_id[name1] = str(id2)

with open('data/name_to_id.json', 'w') as f:
    json.dump(name_to_id, f, indent=4)
