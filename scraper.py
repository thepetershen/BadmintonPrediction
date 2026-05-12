import os 
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
