import pandas as pd
import os

from src.match.scrape_ws_backfill import WS_SIDECAR_DIR, find_tournaments_needing_ws_backfill


# merges a WS-only sidecar file (from scrape_ws_backfill.py) into the original
# MS-only raw tournament csv, tagging the pre-existing rows as match_category="MS"
# so the combined file satisfies REQUIRED_MATCH_COLUMNS in match_proccess.py.
def combine_ms_ws():
  tournaments = find_tournaments_needing_ws_backfill()
  print(f"{len(tournaments)} tournaments to combine.")

  combined_count = 0
  skipped_no_ws_yet = 0

  for tournament_link, tournament_level, slug in tournaments:
    ms_path = "data/rawtournament/" + slug + "_matchdata.csv"
    ws_path = WS_SIDECAR_DIR + slug + "_matchdata.csv"

    df_ms = pd.read_csv(ms_path)
    if 'match_category' in df_ms.columns:
      continue  # already combined

    if not os.path.exists(ws_path):
      skipped_no_ws_yet += 1
      continue

    try:
      df_ws = pd.read_csv(ws_path)
    except pd.errors.EmptyDataError:
      df_ws = pd.DataFrame(columns=df_ms.columns)

    df_ms = df_ms.copy()
    df_ms['match_category'] = 'MS'

    df_combined = pd.concat([df_ms, df_ws], ignore_index=True)
    df_combined.to_csv(ms_path, index=False)
    combined_count += 1

  print(f"Combined {combined_count} tournaments. {skipped_no_ws_yet} still waiting on a WS scrape.")


if __name__ == "__main__":
  combine_ms_ws()
