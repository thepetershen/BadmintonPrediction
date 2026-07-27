
import pandas as pd
import json
from curl_cffi import requests
import time

# open the player data file we already have. 
df = pd.read_csv('data/players_data.csv')
rank_df = pd.read_csv('data/player_rankings.csv')

# We just want to explore the ranks of each player and store it for future reference. 
# set up curl headers
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
# set up years to iterate through
years = ['2022', '2023', '2024', '2025', '2026']
weeks_normal = [str(i) for i in range(1,53)]
weeks_2026 = [str(i) for i in range(1,21)] # since 2026 not over yet. we will use only first 20 weeks. 


# this function takes in a player rank and then populates the dataframe of that players data from 2022 to 2026
def get_player_rank(player_id):
  # duplication check
  existing_records = rank_df[rank_df['ID'] == int(player_id)]
  if not existing_records.empty: # just a general check to see if player scrapped already 
     print("player already exists")
     return

  params['playerId'] = player_id 

  for year in years:
    if (year != '2026') :
      weeks = weeks_normal
    else:
      weeks = weeks_2026

    params['year'] = year
    for week in weeks:

      params['week'] = week

      response = requests.get('https://extranet-lv.bwfbadminton.com/api/player/rankings/history', params=params, headers=headers, impersonate="chrome110")

      # 1. Check if the HTTP request was successful (Status 200)
      if response.status_code != 200:
          print(f"Error {response.status_code}: Failed to fetch data. Skipping...")
          continue 

      # 2. Safely parse the JSON
      try:
          json_data = response.json()
      except ValueError:
          print("Server returned invalid JSON. Skipping...")
          continue

      # 3. Check if 'data' exists AND is not an empty list
      if 'data' not in json_data or len(json_data['data']) == 0:
          print("No ranking data found for this specific query. Skipping...")
          continue

      player_data = json_data['data'][0]

      current_rank = player_data['rank']
      highest_rank = player_data['highest_rank']

      rank_df.loc[len(rank_df)] = [player_id, year, week, current_rank, highest_rank]

  print (player_id + " done")

# loop through the players id df and populate 
for index, row in df.iterrows():
  player_link = row['Player href']

  link = player_link.split("/")

  get_player_rank(link[4])

  time.sleep(20)



# drop duplicates
rank_df = rank_df.drop_duplicates(subset=['ID', 'Week', "Year"], keep='last')

rank_df.to_csv('data/player_rankings.csv', index=False)

