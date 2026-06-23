import os 
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


url = "https://bwfbadminton.com/rankings/?id=2"
driver = webdriver.Chrome()
driver.get(url)

# locates the broser button for the year. 
year_button = driver.find_element(By.XPATH, '//select[@name="year-select"]')
year_button.click()

time.sleep(5)

driver.quit()

conn = psycopg2.connect(
    host="localhost",
    database="badmintondb",
    user="petershen",
    port="5432"
)



