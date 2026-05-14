import os 
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

url = "https://bwfworldtour.bwfbadminton.com/calendar/?cyear=2025&rstate=all"
driver = webdriver.Chrome()
driver.get(url)
time.sleep(5)

conn = psycopg2.connect(
    host="localhost",
    database="badmintondb",
    user="petershen",
    port="5432"
)



