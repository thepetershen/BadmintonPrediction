import pandas as pd
from dataclasses import asdict
import time
import random
import os

import undetected_chromedriver as uc

from src.match.match_scraper import scrape_tournament

WS_SIDECAR_DIR = "data/rawtournament_ws/"


# tournaments whose raw MS csv already exists but has no match_category column
# (i.e. scraped before WS support was added) need a WS-only backfill scrape.
def find_tournaments_needing_ws_backfill():
  df = pd.read_csv('data/all_tournaments.csv')
  needed = []

  for _, row in df.iterrows():
    tournament_link = row['tournament link']
    tournament_level = row['tournament level']
    clean_name_from_link = tournament_link.split('/')[5]
    tournament_path = "data/rawtournament/" + clean_name_from_link + "_matchdata.csv"

    if not os.path.exists(tournament_path):
      continue

    try:
      raw = pd.read_csv(tournament_path)
    except pd.errors.EmptyDataError:
      continue

    if raw.empty or 'match_category' in raw.columns:
      continue

    needed.append((tournament_link, tournament_level, clean_name_from_link))

  return needed


def scrape_ws_backfill():
  month_to_num = {
      "january": 1, "february": 2, "march": 3, "april": 4,
      "may": 5, "june": 6, "july": 7, "august": 8,
      "september": 9, "october": 10, "november": 11, "december": 12
  }

  os.makedirs(WS_SIDECAR_DIR, exist_ok=True)

  tournaments = find_tournaments_needing_ws_backfill()
  print(f"{len(tournaments)} tournaments need a WS backfill scrape.")

  chrome_options = uc.ChromeOptions()
  chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
  driver = uc.Chrome(options=chrome_options, version_main=152)

  for tournament_link, tournament_level, slug in tournaments:
    ws_path = WS_SIDECAR_DIR + slug + "_matchdata.csv"

    if os.path.exists(ws_path):
      print(f"File {ws_path} already exists. Skipping...")
      continue

    matches = []
    tournament_name = scrape_tournament(driver, tournament_link, tournament_level, matches, month_to_num)
    print(tournament_name)

    ws_matches = [m for m in matches if m.match_category == "WS"]
    ws_match_dicts = [asdict(match) for match in ws_matches]

    df_ws_matches = pd.DataFrame(ws_match_dicts)
    df_ws_matches.to_csv(ws_path, index=False)

    random_second = random.randint(10, 20)
    time.sleep(random_second)

  driver.quit()


if __name__ == "__main__":
  scrape_ws_backfill()
