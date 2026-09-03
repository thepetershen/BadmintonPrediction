# BadmintonPrediction

## Description

The purpose of this project is to scrape badminton information off the internet in order to create deep learning models that outperform humans at predicting the outcome of a match.


## Overview / Motivation

I believe that there is a gap in publicly available badminton data. Furthermore, there is nothing except head to head information to predict the outcome of a match. This project aims to change both of those things. I am very passionate about the sport of badminton, so i wish this project can fill in this gap in information.

### Installation

Requires Python 3.

Create a virtual environment and install dependencies into it:

```bash
python3 -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If VSCode's "Run" button or integrated terminal is auto-activating `venv` (this happens automatically once the `venv/` folder exists in the workspace) and a package still isn't found, it means dependencies haven't been installed into that venv yet — run the `pip install -r requirements.txt` step above from inside it.

## Project Structure

```
BadmintonPrediction/
├── data/                             # Scraped/processed data (mostly gitignored CSVs; lookup jsons are tracked)
├── main.py                           # Top-level pipeline entrypoint (scrape -> process -> add features -> train)
├── src/
│   ├── tournament/
│   │   └── tournament_scraper.py     # Scrapes tournament listings from the bwfbadminton.com calendar
│   ├── match/
│   │   ├── match_scraper.py          # Scrapes MS/WS match results within a tournament
│   │   ├── scrape_ws_backfill.py     # Backfills WS-only matches for tournaments scraped before WS support existed
│   │   ├── combine_ms_ws.py          # Merges backfilled WS matches into the original MS-only raw tournament CSVs
│   │   ├── match_proccess.py         # Compiles raw tournament CSVs into the master match dataset, incl. rank lookups
│   │   ├── rank_lookup.py            # Queries BWF's ranking API for a player's rank at a given week
│   │   ├── name_to_id.py             # Builds the combined name -> id lookup from the master match files
│   │   └── models.py                 # Dataclasses for match records
│   ├── features/
│   │   ├── add_features.py           # Builds Elo/head-to-head/rank-diff features for training
│   │   └── split_ms_ws_names.py      # Splits the name -> id lookup into separate MS/WS files
│   ├── training/
│   │   ├── train_RF.py               # Trains a Random Forest model
│   │   ├── train_XGB.py              # Trains an XGBoost model
│   │   ├── train_GNN.py              # Trains a GNN model
│   │   └── test_models.py            # Model evaluation/testing
│   ├── server/
│   │   └── app.py                    # FastAPI backend: serves player lists and matchup predictions
│   ├── frontend/                     # React (Vite) frontend for submitting matchups and viewing predictions
│   │   └── src/
│   │       ├── App.jsx
│   │       ├── SearchComponent.jsx        # Category (MS/WS) + player selection, submits the matchup
│   │       ├── PlayerDropdownComponent.jsx
│   │       └── ExpectedWinnerComponent.jsx
│   └── outdated/                     # Legacy scrapers no longer used in the active pipeline
└── License.md
```

## License

See [License.md](License.md).
