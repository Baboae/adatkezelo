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

@dataclass
class Lap:
    """Represents a single lap in a race."""
    position: int
    incidents: int
    valid: bool
    time: float  # lap time in seconds

@dataclass
class RaceResult:
    """Stores the results of a race for a given player."""
    RACE_ID: str
    USER_ID: int
    laps: List[Lap]

    def best_lap(self) -> Optional[Lap]:
        """Return the fastest valid lap, if any."""
        valid_laps = [lap for lap in self.laps if lap.valid]
        return min(valid_laps, key=lambda lap: lap.time) if valid_laps else None

    def total_incidents(self) -> int:
        """Return the total number of incidents across all laps."""
        return sum(lap.incidents for lap in self.laps)

    def average_time(self) -> Optional[float]:
        """Return the average time of valid laps."""
        valid_times = [lap.time for lap in self.laps if lap.valid]
        return sum(valid_times) / len(valid_times) if valid_times else None
