import os 
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import undetected_chromedriver as uc


url = "https://bwfbadminton.com/rankings/?id=2"

# use the hidden chromebrower as to not get blocked. 

chrome_options = uc.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = uc.Chrome(options=chrome_options, version_main=149)
driver.get(url)

time.sleep(3)

# checks for if there are cookies that need to be declines
try:
  time.sleep(3)
  decline_button = driver.find_element(By.ID, "cookiescript_reject")
  decline_button.click()
except Exception as e:
  print ("no cookies")

def get_page_players():
  # locates the elements that represent the rows of players (each being a plyer)
  players = driver.find_elements(By.XPATH, '//tr')

  for player in players:
    try:
      # gets the embedded player name column
      player_col = player.find_element(By.XPATH, './/td[@class="col-player"]')


      # gets the specifc player name wrapper
      player_link = player_col.find_element(By.XPATH, ".//a")

      raw_name = player_col.text

      print (raw_name)

    
    except Exception as e:
      print(f"Skipping row due to formatting issue: {e}")
      continue 

for i in range (0, 4):
   
  get_page_players()

  time.sleep(3)

  nav_bar = driver.find_element(By.XPATH, '//nav[@class="pagination"]')

  next_page_btn = nav_bar.find_element(By.XPATH, './/a[i[contains(@class, "fa-chevron-right")]]')
  driver.execute_script("arguments[0].click();", next_page_btn)

  time.sleep(3)



# stall forever for us to see browser.
input("Press Enter in the terminal to close the browser...")





