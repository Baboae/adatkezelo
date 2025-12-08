from dataclasses import dataclass
from typing import List, Optional, Dict, Any

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

@dataclass
class Lap:
    lap: int
    time: int
    valid: bool
    position: int
    incidents: List[str]

@dataclass
class ParticipantResult:
    user_id: int
    username: str
    start_position: int
    finish_position: int
    incident_points: int
    total_time: int
    results: Dict[str, float]   # rating_before, reputation_before, rating_change, reputation_change
    laps: List[Lap]
    new_rating: float = 0.0
    new_rep: float = 0.0

@dataclass
class RaceResult:
    race_id: str
    track: str
    layout: str
    car_class: str
    participants: List[ParticipantResult]