import pandas as pd 
import time

from dataclasses import dataclass
from typing import Optional
from datetime import date

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# this defines a Match Record class which will be used as a template for adding a match
@dataclass
class MatchRecord:
    tournament_name: str
    tournament_level: str
    match_date: date
    round_name: str
    
    player_1: str
    player_2: str
    
    winner_name: str
    score: str

    duration_minutes: Optional[int] = None
    match_id: Optional[str] = None


chrome_options = uc.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = uc.Chrome(options=chrome_options, version_main=149)

# get the already scraped list of all tournaments
df = pd.read_csv('data/all_tournaments.csv')

matches = []

# cookie check
def cookie_check():
  try:
    time.sleep(3)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")

# takes in a given id and scrapes that tournament specifically. 
def scrape_tournament(link):
  cookie_check()
  driver.get(link)
  day_all = driver.find_element(By.XPATH, '//ul[@id="ajaxTabsResults"]')
  day_all_iter = day_all.find_elements(By.XPATH, './li')
  
  # this goes through each element of day
  for day in day_all_iter:
    day.click() # switch to it

    time.sleep(3)

    #list of all matches on the screen
    all_matches_screen = driver.find_element(By.XPATH, '//div[@class="match-card"]')

    for cur_read_match in all_matches_screen:
      # get the m



  return

for index, row in df.iterrows():
  player_link = row['tournamentLink']

  scrape_tournament(player_link)

  time.sleep(20)
