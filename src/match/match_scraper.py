import pandas as pd 
from dataclasses import asdict
import time

from src.match.models import MatchRecord
from datetime import date

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

import re
import random
import os



# cookie check
def cookie_check(driver):
  try:
    time.sleep(8)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")

# this function proccesses the name of a bwf tournament and returns importnat elements. 
def clean_tournament_name(raw_name: str):
    # 1. Convert to lowercase to locate the starting index of sponsor keywords
    lower_name = raw_name.lower()
    
    # 2. Check for keywords and get the starting index
    sponsor_index = -1
    for keyword in ["presented by", "powered by"]:
        idx = lower_name.find(keyword)
        if idx != -1:
            sponsor_index = idx
            break
            
    # 3. Slice the string up to the sponsor index if found
    if sponsor_index != -1:
        raw_name = raw_name[:sponsor_index]

    # 4. Find the 4-digit year from what's left
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', raw_name)
    clean_year = year_match.group(1) if year_match else ""

    # 5. Remove the year from the string to isolate the tournament name
    clean_name = re.sub(r'\b(19\d{2}|20\d{2})\b', '', raw_name)

    # 6. Strip remaining double spaces and whitespace
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()

    return clean_name, clean_year

# takes in a given id and scrapes that tournament specifically. 
def scrape_tournament(driver, link, level, matches, month_to_num):
  driver.get(link)
  cookie_check(driver)
  
  time.sleep(5) 
  
  #find the tournament name
  tournament_information = driver.find_element(By.XPATH, '//div[@class="live-tournament-wrapper"]')
  tournament_name= tournament_information.find_element(By.XPATH, './h2').text
  tournament_date = tournament_information.find_element(By.XPATH, './div[@class="live-date"]').text

  tournament_name_clean, tournament_year_clean = clean_tournament_name(tournament_name)

  tournament_date = tournament_date.split(" ")
  start_day = int(tournament_date[0])

  # 2. Determine the start month based on the list length
  if len(tournament_date) == 5:
      start_month_str = tournament_date[1]
  elif len(tournament_date) == 4:
      start_month_str = tournament_date[3]
  else:
      start_month_str = tournament_date[1] 

  start_month = month_to_num[start_month_str.lower()]

  date_of_tournament = date(int(tournament_year_clean), start_month, start_day)

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
      if match_type != "MS" and match_type != "WS":
        continue
      round_info = footer_items[2].text.strip()

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

      # now we need to scrape the scores of the participants. 

      score_section = cur_read_match.find_element(By.XPATH, './/div[@class="game-score-module-wrapper"]')
      score_games = score_section.find_elements(By.XPATH, './div[@class="game-score-set"]')

      if len(score_games) == 0:
        print ("Skipppped")
        continue # not sure why it would ever be empty
      elif len (score_games) == 1:
        game1 = score_games[0]

        game1_scores = game1.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game1_player1_score = game1_scores[0].text
        game1_player2_score = game1_scores[1].text

        new_match = MatchRecord(tournament_name=tournament_name_clean, tournament_level=level, match_date=date_of_tournament,
                                round_name=round_info, match_category=match_type, player_1_id=player1_id, player_2_id=player2_id,
                                winner_id=winner, g1_p1_score=game1_player1_score, g1_p2_score=game1_player2_score)
        matches.append(new_match)
      elif len(score_games) == 2:
        game1 = score_games[0]
        game2 = score_games[1]

        game1_scores = game1.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game1_player1_score = game1_scores[0].text
        game1_player2_score = game1_scores[1].text

        game2_scores = game2.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game2_player1_score = game2_scores[0].text
        game2_player2_score = game2_scores[1].text

        new_match = MatchRecord(tournament_name=tournament_name_clean, tournament_level=level, match_date=date_of_tournament,
                                        round_name=round_info, match_category=match_type, player_1_id=player1_id, player_2_id=player2_id,
                                        winner_id=winner, g1_p1_score=game1_player1_score, g1_p2_score=game1_player2_score,
                                        g2_p1_score=game2_player1_score, g2_p2_score= game2_player2_score)
        matches.append(new_match)

      elif len(score_games) == 3:
        game1 = score_games[0]
        game2 = score_games[1]
        game3 = score_games[2]

        game1_scores = game1.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game1_player1_score = game1_scores[0].text
        game1_player2_score = game1_scores[1].text

        game2_scores = game2.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game2_player1_score = game2_scores[0].text
        game2_player2_score = game2_scores[1].text

        game3_scores = game3.find_elements(By.XPATH, './span[contains(@class, "set-points")]')
        game3_player1_score = game3_scores[0].text
        game3_player2_score = game3_scores[1].text

        new_match = MatchRecord(tournament_name=tournament_name_clean, tournament_level=level, match_date=date_of_tournament, 
                                                round_name=round_info, match_category=match_type,player_1_id=player1_id, player_2_id=player2_id,
                                                winner_id=winner, g1_p1_score=game1_player1_score, g1_p2_score=game1_player2_score,
                                                g2_p1_score=game2_player1_score, g2_p2_score= game2_player2_score,
                                                g3_p1_score= game3_player1_score, g3_p2_score=game3_player2_score)
        matches.append(new_match)
      else:
        continue

  return tournament_name

def scrape_match():
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
  driver = uc.Chrome(options=chrome_options, version_main=152)

  # get the already scraped list of all tournaments
  df = pd.read_csv('data/all_tournaments.csv')

  for index, row in df.iterrows():
    tournament_link = row['tournament link']
    tournament_level = row["tournament level"]
    clean_name_from_link = tournament_link.split('/')[5]
    tournament_path = "data/rawtournament/" + clean_name_from_link + "_matchdata.csv"

    if os.path.exists(tournament_path):
      print(f"File {tournament_path} already exists. Skipping...")
      continue

    matches = []
    tournament_name = scrape_tournament(driver, tournament_link, tournament_level, matches, month_to_num)
    print(tournament_name)
    
    match_dicts = [asdict(match) for match in matches]

    df_matches = pd.DataFrame(match_dicts) # directly convert dictionary to dataframe

    df_matches.to_csv(tournament_path, index=False)
    # random sleep. 
    random_second = random.randint(10, 20)
    time.sleep(random_second)
  

if __name__ == "__main__":
  scrape_match()