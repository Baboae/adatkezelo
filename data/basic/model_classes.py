from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Player:
    USER_ID: int
    username: str
    full_name: str
    nationality: str
    team: str
    elo_rating: float = 1500
    reputation: float = 75
    race_count: int = 0

@dataclass
class Race_Data:
    RACE_ID: str
    track: str
    layout: str
    car_class: str
    timestamp: int   # új mező: UNIX epoch ms

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
    results: Dict[str, float]
    laps: List[Lap]
    new_rating: float = 0.0
    new_rep: float = 0.0

@dataclass
class RaceResult:
    race_id: str
    track: str
    layout: str
    car_class: str
    timestamp: int   # új mező: UNIX epoch ms
    participants: List[ParticipantResult]
