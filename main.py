import datetime
from typing import List
from data.basic.model_classes import *
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data


def LTF(ms: int) -> str: #LAP TIME FORMATTER
    """Convert lap time in milliseconds to M:SS.mmm format."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"
def DTF(dt: datetime) -> str: #DATE TIME FORMATTER
    """Convert datetime object to YYYY-MM-DD HH:MM:SS format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def main():
    PLAYERS = generate_players(32)
    players: List[Player] = []
    for p in PLAYERS:
        players.append(p)

    RDS = generate_race_data(24)
    race_metas: List[Race_Data] = []
    for r in RDS:
        race_metas.append(r)
    for r in race_metas:
        print(r)
if __name__ == '__main__':
    main()