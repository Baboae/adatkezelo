from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Player:
    """Contains basic and ranked information about the player."""
    USER_ID: int
    username: str
    full_name: str
    nationality: str
    team: str
    elo_rating: float = 1500  # starts at 1500
    reputation: float = 75  # starts at 75, max 100
    race_count: int = 0 #num of races they took part in

@dataclass
class Race_Data:
    """Contains essential details about a race."""
    RACE_ID: str
    track: str
    layout: str
    car_class: str