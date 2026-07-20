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
    tournament_level: int
    match_date: date
    round_name: str
    
    player_1_id: str
    player_2_id: str
    winner_id: str
    
    # Game 1
    g1_p1_score: int
    g1_p2_score: int
    
    # Game 2
    g2_p1_score: int
    g2_p2_score: int
    
    # Game 3 (Optional for straight-set matches)
    g3_p1_score: Optional[int] = None
    g3_p2_score: Optional[int] = None

month_to_num = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}

chrome_options = uc.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = uc.Chrome(options=chrome_options, version_main=149)

# get the already scraped list of all tournaments
df = pd.read_csv('data/all_tournaments.csv')

matches = []

# cookie check
def cookie_check():
  try:
    time.sleep(8)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")

# takes in a given id and scrapes that tournament specifically. 
def scrape_tournament(link):
  driver.get(link)
  cookie_check()
  
  time.sleep(5) 
  
  #find the tournament name
  tournament_information = driver.find_element(By.XPATH, '//div[@class="live-tournament-wrapper"]')
  tournament_name= tournament_information.find_element(By.XPATH, './h2').text
  tournament_date = tournament_information.find_element(By.XPATH, './div[@class="live-date"]').text

  tournament_name_clean = tournament_name[:-5]
  tournament_year_clean = tournament_name[-5:]

  tournament_date = tournament_date.split(" ")

  date_of_tournament = date(int(tournament_year_clean), month_to_num[str.lower(tournament_date[3])], int(tournament_date[0]))
  print(tournament_name_clean)
  print(date_of_tournament)

  # Find how many tabs exist
  day_all = driver.find_element(By.XPATH, '//ul[@id="ajaxTabsResults"]')
  number_of_tabs = len(day_all.find_elements(By.XPATH, './li'))
  
  
  for i in range(number_of_tabs - 1):
      
    fresh_tabs_list = driver.find_element(By.XPATH, '//ul[@id="ajaxTabsResults"]').find_elements(By.XPATH, './li')
    current_tab = fresh_tabs_list[i]
    clickable_link = current_tab.find_element(By.XPATH, './/a')
    driver.execute_script("arguments[0].click();", clickable_link)
    driver.execute_script("arguments[0].click();", current_tab)
    
    # Give the matches time to load after clicking the tab
    time.sleep(5)

    all_matches_screen = driver.find_elements(By.XPATH, '//div[contains(@class, "match-card-wrapper")]')

    for cur_read_match in all_matches_screen:
      
      footer = cur_read_match.find_element(By.XPATH, './/div[contains(@class, "footer-wrapper")]')

      footer_items = footer.find_elements(By.TAG_NAME, 'span')

      # understand the type of match, for our use case we are only scarping MS
      match_type = footer_items[0].text.strip() 
      if match_type != "MS":
        continue
      round_info = footer_items[1].text.strip() 

      #if we got here, we can create a match object
      # first we need to scrape the names of each player (specifically their ids)

      players_section = cur_read_match.find_element(By.XPATH, './/div[@class="participants-details-wrapper"]')
      player_wrappers = players_section.find_elements(By.XPATH, './div')
      player1_wrapper = player_wrappers[0]
      player2_wrapper = player_wrappers[2]

      player1_a_element = player1_wrapper.find_element(By.XPATH, ".//a")
      player2_a_element = player2_wrapper.find_element(By.XPATH, ".//a")

      player1_href = player1_a_element.get_attribute("href")
      player2_href = player2_a_element.get_attribute("href")
      player1_href_split = player1_href.split("/")
      player2_href_split = player2_href.split("/")

      player1_id = player1_href_split[4]
      player2_id = player2_href_split[4]

      # we will do a simple trick to find out the winner
      winner_dots = player1_wrapper.find_elements(By.XPATH, './/div[contains(@class, "winner-dot")]')
      winner = player2_id
      if len(winner_dots) > 0:
        winner = player1_id

      print(winner)
      print(player1_id)



      

  return

scrape_tournament("https://bwfworldtour.bwfbadminton.com/tournament/4426/yonex-sunrise-india-open-2022/results/")

# for index, row in df.iterrows():
#   player_link = row['tournamentLink']

#   scrape_tournament(player_link)

#   time.sleep(20)
