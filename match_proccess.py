import pandas as pd
from dataclasses import dataclass
from typing import Optional
from datetime import date
import time
from dataclasses import asdict
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from curl_cffi import requests

# we will aim to create 2 files. 1 where names are proccessed and one where they are not. (for publishing vs our use)
# we will take use the player ids to perform looks of their name in df. If it doesn't exist, we will scrape it.
id_to_name = {}

# we need to be able to know the ranks of each players. since it has each week, we need to update, we go from past to present, and each tournament 1 week max, so we will use
# the last needed week, if a new match is introduced, it is assumed that it will never go back

@dataclass
class MatchRecordPublish:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  
  player_1_name: str
  player_2_name: str
  winner_name: str

  player_1_rank: int
  player_2_rank: int
  player_1_rank_highest: int
  player_2_rank_highest: int

  # Game 1
  g1_p1_score: int
  g1_p2_score: int
  
  # Game 2 also optional in the case of retirement
  g2_p1_score: Optional[int] = None
  g2_p2_score: Optional[int] = None
  
  # Game 3 (Optional for straight-set matches)
  g3_p1_score: Optional[int] = None
  g3_p2_score: Optional[int] = None

@dataclass
class MatchRecord:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  
  player_1_id: int
  player_2_id: int
  winner_id: str

  player_1_rank: int
  player_2_rank: int
  player_1_rank_highest: int
  player_2_rank_highest: int

  # Game 1
  g1_p1_score: int
  g1_p2_score: int
  
  # Game 2 also optional in the case of retirement
  g2_p1_score: Optional[int] = None
  g2_p2_score: Optional[int] = None
  
  # Game 3 (Optional for straight-set matches)
  g3_p1_score: Optional[int] = None
  g3_p2_score: Optional[int] = None

chrome_options = uc.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = uc.Chrome(options=chrome_options, version_main=149)

# stores all matches with id
all_matches = []
# stores all matches with name of player
all_matches_publish = []

# these are for requesting the rank of the player to the internal api
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


def cookie_check():
  try:
    time.sleep(8)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")

# takes in the player id and the date of the tournament and returns the current and highest rank of the  player at that point. 
def get_rank(playerid, tournament_year, tournament_week):
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

def reformat_tournament(file_path):

  df = pd.read_csv(file_path, parse_dates=['match_date'])

  tracked_year, tracked_week = 0, 0
  # we will track a dictionary of their ids to a tuple, being their ranks and highest rank
  rankings = {}

  # goes through every match
  for index, row in df.iterrows():
    player_id_1 = row["player_1_id"]
    player_id_2 = row["player_2_id"]

    tournament_date = row['match_date']
    tournament_week = tournament_date.isocalendar().week
    tournament_year = tournament_date.year

    # essentially uses a dictional to store all the ids of the plaeyers, if they exist then we don't find it again
    if player_id_1 in id_to_name:
      full_name_1 = id_to_name.get(player_id_1)
    else:
      link_player_1 = "https://bwfbadminton.com/player/" + str(player_id_1)

      driver.get(link_player_1)
      cookie_check()

      full_name_element = driver.find_element(By.XPATH, './/div[@class="playertop-name"]')
      last_name = full_name_element.find_element(By.XPATH, './/span[@class="name-2"]').text.strip()
      first_name = full_name_element.find_element(By.XPATH, './/span[@class="name-1"]').text.strip()

      full_name_1 = first_name + " " + last_name

      id_to_name[player_id_1] = full_name_1

    if player_id_2 in id_to_name:
      full_name_2 = id_to_name.get(player_id_2)
    else:
      link_player_2 = "https://bwfbadminton.com/player/" + str(player_id_2)

      driver.get(link_player_2)
      cookie_check()

      full_name_element = driver.find_element(By.XPATH, './/div[@class="playertop-name"]')
      last_name = full_name_element.find_element(By.XPATH, './/span[@class="name-2"]').text.strip()
      first_name = full_name_element.find_element(By.XPATH, './/span[@class="name-1"]').text.strip()

      full_name_2 = first_name + " " + last_name

      id_to_name[player_id_2] = full_name_2

    if player_id_1 == row["winner_id"]:
      winner_name = full_name_1
    else:
      winner_name = full_name_2

    # if we are still on the current week of the tournament
    if tournament_week == tracked_week and tournament_year == tracked_year:
      player_1_cur_rank, player_1_highest_rank = rankings.get(player_id_1, (None, None))
      player_2_cur_rank, player_2_highest_rank = rankings.get(player_id_2, (None, None))

      if player_1_cur_rank is None or player_1_highest_rank is None:
          player_1_cur_rank, player_1_highest_rank = get_rank(player_id_1, tournament_year, tournament_week)
          rankings[player_id_1] = (player_1_cur_rank, player_1_highest_rank)
          
      if player_2_cur_rank is None or player_2_highest_rank is None:
          player_2_cur_rank, player_2_highest_rank = get_rank(player_id_2, tournament_year, tournament_week)
          rankings[player_id_2] = (player_2_cur_rank, player_2_highest_rank)
          
    else: 
      # else reset all the data we have
      rankings = {}
      tracked_week = tournament_week
      tracked_year = tournament_year
      
      player_1_cur_rank, player_1_highest_rank = get_rank(player_id_1, tournament_year, tournament_week)
      rankings[player_id_1] = (player_1_cur_rank, player_1_highest_rank)
      
      player_2_cur_rank, player_2_highest_rank = get_rank(player_id_2, tournament_year, tournament_week)
      rankings[player_id_2] = (player_2_cur_rank, player_2_highest_rank)

    new_published_match = MatchRecordPublish(
      tournament_name=row['tournament_name'],
      tournament_level=row['tournament_level'],
      match_date=row['match_date'],
      round_name=row['round_name'],
      
      g1_p1_score=row['g1_p1_score'],
      g1_p2_score=row['g1_p2_score'],
      g2_p1_score=row.get('g2_p1_score'), 
      g2_p2_score=row.get('g2_p2_score'),
      g3_p1_score=row.get('g3_p1_score'),
      g3_p2_score=row.get('g3_p2_score'),

     
      player_1_name=full_name_1,               
      player_2_name=full_name_2,               
      winner_name=winner_name,            
      
      player_1_rank=player_1_cur_rank,        
      player_2_rank=player_2_cur_rank,        
      player_1_rank_highest=player_1_highest_rank, 
      player_2_rank_highest=player_2_highest_rank
    )

    new_match = MatchRecord(
      tournament_name=row['tournament_name'],
      tournament_level=row['tournament_level'],
      match_date=row['match_date'],
      round_name=row['round_name'],
      
      g1_p1_score=row['g1_p1_score'],
      g1_p2_score=row['g1_p2_score'],
      g2_p1_score=row.get('g2_p1_score'), 
      g2_p2_score=row.get('g2_p2_score'),
      g3_p1_score=row.get('g3_p1_score'),
      g3_p2_score=row.get('g3_p2_score'),

      
      player_1_id=player_id_1,               
      player_2_id=player_id_2,               
      winner_id=row['winner_id'],            
      
      player_1_rank=player_1_cur_rank,        
      player_2_rank=player_2_cur_rank,        
      player_1_rank_highest=player_1_highest_rank, 
      player_2_rank_highest=player_2_highest_rank
    )

    all_matches.append(new_match)
    all_matches_publish.append(new_published_match)
  

  return

df_tournaments = pd.read_csv("data/all_tournaments.csv")

for index, row in df_tournaments.iterrows():
  tournament_link = row['tournament link']
  clean_name_from_link = tournament_link.split('/')[5]
  tournament_path = "data/rawtournament/" + clean_name_from_link + "_matchdata.csv"
  reformat_tournament(tournament_path)


all_match_dicts = [asdict(match) for match in all_matches]
all_match_publish_dicts = [asdict(match) for match in all_matches_publish]

df_matches = pd.DataFrame(all_match_dicts) # directly convert dictionary to dataframe
df_matches_publish = pd.DataFrame(all_match_publish_dicts)
df_matches.to_csv("data/all_match_id.csv", index=False)
df_matches_publish.to_csv("data/all_match_name.csv", index=False)



driver.quit()