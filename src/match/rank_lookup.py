from curl_cffi import requests
# takes in the player id and the date of the tournament and returns the current and highest rank of the  player at that point. 
def get_rank(playerid, tournament_year, tournament_week, params, headers):
  # first we must reformat the date into a month and week/

  params['playerId'] = playerid
  params['year'] = tournament_year
  params['week'] = tournament_week

  response = requests.get('https://extranet-lv.bwfbadminton.com/api/player/rankings/history', params=params, headers=headers, impersonate="chrome110")

  if response.status_code != 200:
    print(f"Error {response.status_code}: Failed to fetch data. Skipping...")
    return (None, None)

  # 2. Safely parse the JSON
  try:
    json_data = response.json()
  except ValueError:
    print("Server returned invalid JSON. Skipping...")
    return(None, None)

  # 3. Check if 'data' exists AND is not an empty list
  if 'data' not in json_data or len(json_data['data']) == 0:
    print("No ranking data found for this specific query. Skipping...")
    return(None, None)

  player_data = json_data['data'][0]

  cur_rank = player_data['rank']
  highest_rank = player_data['highest_rank']

  return cur_rank, highest_rank