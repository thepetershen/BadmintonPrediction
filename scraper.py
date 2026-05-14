import os 
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="badmintondb",
    user="petershen",
    port="5432"
)