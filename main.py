from src.match.match_proccess import process_matches
from src.match.match_scraper import scrape_match
from src.tournament.tournament_scraper import scrape_tournaments
from src.features.add_features import add_features
from src.training.train_RF import train_RF
from src.training.train_XGB import train
from src.training.train_GNN import train_gnn

if __name__ == "__main__":
    # scrape_tournaments()
    # scrape_match()
    process_matches()

    # add_features()

    # train_RF()
    # train()
    # train_gnn()

    # test_all()
    # test_xgb_symmetry()
