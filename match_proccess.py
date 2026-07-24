import pandas as pd

from dataclasses import dataclass
from typing import Optional
from datetime import date

import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# we will aim to create 2 files. 1 where names are proccessed and one where they are not. (for publishing vs our use)
# we will take use the player ids to perform looks of their name in df. If it doesn't exist, we will scrape it.
id_to_name = {}

# 

@dataclass
class MatchRecordPublish:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  
  player_1_name: str
  player_2_name: str
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
def cookie_check():
  try:
    time.sleep(8)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")
  
def reformat_tournament(file_path):

  df = pd.read_csv(file_path)

  for index, row in df.iterrows():
    player_id_1 = row["player_1_id"]
    player_id_2 = row["player_2_id"]

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

      id_to_name[player_id_1] = full_name_2

    print(full_name_1)
    print(full_name_2)


    

  return

reformat_tournament("data/rawtournament/2022-gwangju-yonex-korea-masters_matchdata.csv")

driver.quit()