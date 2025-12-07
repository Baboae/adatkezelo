import datetime
import random
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_lap_generator import generate_race_laps

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
    print("\n")
    players = generate_players(3)
    rds = generate_race_data(3)
    rls = generate_race_laps(players, rds[0], 3)
    for p in players:
        print(p)
    print("\n")
    for r in rds:
        print(r)
    print("\n")
    for rl in rls:
        print(f"R{rl.RACE_ID}"
              f"\nUser #{rl.user_id} went: {LTF(rl.laptime)}")
if __name__ == '__main__':
    main()