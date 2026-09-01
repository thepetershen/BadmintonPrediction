from dataclasses import dataclass
from typing import Optional
from datetime import date

# this defines a Match Record class which will be used as a template for adding a match
@dataclass
class MatchRecord:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  match_category: str
  
  player_1_id: str
  player_2_id: str
  winner_id: str
  
  # Game 1
  g1_p1_score: int
  g1_p2_score: int
  
  # Game 2 also optional in the case of retirement
  g2_p1_score: Optional[int] = None
  g2_p2_score: Optional[int] = None
  
  # Game 3 (Optional for straight-set matches)
  g3_p1_score: Optional[int] = None
  g3_p2_score: Optional[int] = None

@dataclass
class MatchRecordPublish:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  match_category: str
  
  player_1_name: str
  player_2_name: str
  winner_name: str

  player_1_rank: int
  player_2_rank: int
  player_1_rank_highest: int
  player_2_rank_highest: int

  # Game 1
  g1_p1_score: int
  g1_p2_score: int
  
  # Game 2 also optional in the case of retirement
  g2_p1_score: Optional[int] = None
  g2_p2_score: Optional[int] = None
  
  # Game 3 (Optional for straight-set matches)
  g3_p1_score: Optional[int] = None
  g3_p2_score: Optional[int] = None

@dataclass
class MatchRecordRanked:
  tournament_name: str
  tournament_level: int
  match_date: date
  round_name: str
  match_category: str
  
  player_1_id: int
  player_2_id: int
  winner_id: str

  player_1_rank: int
  player_2_rank: int
  player_1_rank_highest: int
  player_2_rank_highest: int

  # Game 1
  g1_p1_score: int
  g1_p2_score: int
  
  # Game 2 also optional in the case of retirement
  g2_p1_score: Optional[int] = None
  g2_p2_score: Optional[int] = None
  
  # Game 3 (Optional for straight-set matches)
  g3_p1_score: Optional[int] = None
  g3_p2_score: Optional[int] = None
