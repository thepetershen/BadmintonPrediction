import pandas as pd
import json
from curl_cffi import requests

# open the player data file we already have. 
df = pd.read_csv('data/players_data.csv')

# We just want to explore the ranks of each player and store it for future reference. 

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

response = requests.get('https://extranet-lv.bwfbadminton.com/api/player/rankings/history', params=params, headers=headers, impersonate="chrome110")

json_data = response.json()

player_data = json_data['data'][0]

current_rank = player_data['rank']
highest_rank = player_data['highest_rank']

print(f"Current Rank: {current_rank}")
print(f"Highest Rank: {highest_rank}")



