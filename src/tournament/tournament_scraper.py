
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains # for weird close out

import time

import pandas as pd


def get_page_tournaments (driver, tournaments, tournaments_levels):
  
  tournament_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "tmt-card")]')

  for tournament_card in tournament_cards:
   if tournament_card.is_displayed():       
    link_element = tournament_card.find_element(By.XPATH, ".//a")
    link_href = link_element.get_attribute('href')
    
    all_text = tournament_card.find_element(By.XPATH, './/div[@class="text-info"]')
    tournament_level_prize = all_text.find_elements(By.XPATH, './/div[@class="labels"]')
    tournament_level = tournament_level_prize[1].find_elements(By.XPATH, "./div")
    tournament_level = tournament_level[0].text
    tournament_level = tournament_level.split()
    tournament_level = tournament_level[-1]

    if not link_href in tournaments:
      tournaments.append(link_href)
      tournaments_levels.append(tournament_level)

    

def next_page(driver):
  time.sleep(3)

  nav_bar = driver.find_element(By.XPATH, '//nav[@class="pagination"]')

  next_page_btn = nav_bar.find_element(By.XPATH, './/a[i[contains(@class, "fa-chevron-right")]]')
  driver.execute_script("arguments[0].click();", next_page_btn)

  time.sleep(3)

def cookie_check(driver):
  try:
    time.sleep(3)
    decline_button = driver.find_element(By.ID, "cookiescript_reject")
    decline_button.click()
  except Exception as e:
    print ("no cookies")


# set the correct filters for the page (the right time period)
def filter_page(driver):

  wait = WebDriverWait(driver, 10)
  
  # click on all tournaments tab
  tournament_button = driver.find_element(By.LINK_TEXT, "ALL TOURNAMENTS")
  tournament_button.click()

  time.sleep(3)

  #clear the current filter
  date_filter = driver.find_elements(By.XPATH,  "//button[@aria-label='clear icon']")
  date_filter[1].click()
  date_filter[2].click()
  time.sleep(1)

  #send in date filters
  date_input = driver.find_elements(By.XPATH,  "//input[@placeholder='click to select date']")
  date_input[0].send_keys("01/01/2018")
  date_input[1].send_keys("01/05/2026")

  time.sleep(1)

  level_dropdown = driver.find_element(
      By.XPATH, '//div[contains(@class, "v-select__slot")][.//label[contains(text(), "Level")]]'
    )
  level_dropdown.click()

  time.sleep(2)

  options = driver.find_elements(
      By.XPATH, '//div[contains(@class, "menuable__content__active")]//div[@role="option"]'
  )

  # Select your multiple events
  options[8].click()
  time.sleep(0.5) 
  options[9].click()
  time.sleep(0.5) 
  options[10].click()
  time.sleep(0.5) 
  options[11].click()
  time.sleep(0.5)

  #close out
  level_input = driver.find_element(By.XPATH, '//div[contains(@class, "v-select__slot")][.//label[contains(text(), "Level")]]//input')
  level_input.send_keys(Keys.TAB)
  time.sleep(1) # Give it time to animate closed

  options_dropdown = driver.find_element(By.XPATH, '//div[contains(@class, "v-select__slot")][.//label[contains(text(), "Status")]]')
  options_dropdown.click()

  time.sleep(1)
  options = driver.find_elements(
    By.XPATH, '//div[contains(@class, "menuable__content__active")]//div[@role="option"]'
  )
  options[2].click()
  time.sleep(0.5) 

  # close out
  options_dropdown.click()

  time.sleep(3) 




def scrape_tournaments():
  url = "https://bwfbadminton.com/calendar/"

  # use the hidden chromebrower as to not get blocked. 
  chrome_options = uc.ChromeOptions()
  chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
  driver = uc.Chrome(options=chrome_options, version_main=152)
  driver.get(url)

  time.sleep(3)

  # all tournaments
  tournaments = []
  tournaments_levels = []


  cookie_check(driver)

  filter_page(driver)

  # we will loop through all 22 pages, clicking next 21 times total

  for i in range (0, 21):
    get_page_tournaments(driver, tournaments, tournaments_levels)

    next_page(driver)

  get_page_tournaments(driver, tournaments, tournaments_levels)

  df = pd.DataFrame({"tournament link": tournaments, "tournament level": tournaments_levels})
  df.to_csv("data/all_tournaments.csv", index = False)

  driver.quit()

if __name__ == "__main__":
  scrape_tournaments()