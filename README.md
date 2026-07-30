# BadmintonPrediction

## Description

The purpose of this project is to scrape badminton information off the internet in order to create deep learning models that outperform humans at predicting the outcome of a match.


## Overview / Motivation

I believe that there is a gap in publicly available badminton data. Furthermore, there is nothing except head to head information to predict the outcome of a match. This project aims to change both of those things. I am very passionate about the sport of badminton, so i wish this project can fill in this gap in information.

### Installation

Requires Python 3.

```bash
pip install selenium undetected-chromedriver pandas psycopg2-binary python-dotenv
```

## Project Structure

```
BadmintonPrediction/
├── data/                          # Scraped/processed data (CSV outputs)
├── src/
│   ├── tournament/
│   │   ├── tournament_scraper.py  # Scrapes tournament listings from bwfbadminton.com
│   │   ├── match_scraper.py       # Scrapes individual match results within tournaments
│   │   └── match_proccess.py      # Processes/compiles scraped match data
│   └── player/
│       ├── player_scraper.py      # Scrapes player data
│       └── player_rank_scraper.py # Scrapes player rankings
└── License.md
```

## Setup

<!-- TODO: flesh out once a main entry point is created -->
 No database is set up yet; data is currently written to local CSV files in `data/`.

## Roadmap

Currently scrapped informaiton, working on building very first model. 
## License

See [License.md](License.md).
