from src.match.match_proccess import process_matches
from src.match.match_scraper import scrape_match
from src.tournament.tournament_scraper import scrape_tournaments

if __name__ == "__main__":
    scrape_tournaments()
    scrape_match()
    process_matches()