import json
import random
import string
from datetime import datetime, timedelta
from typing import List
from data.basic.model_classes import Race_Data

START_DATE = datetime(2025, 11, 24, 14, 0, 0)
END_DATE = datetime(2025, 11, 30, 23, 59, 59)

def _random_start_time() -> int:
    """
    Generál egy random időpontot 2025-11-24 14:00 és 2025-11-30 01:30 között.
    Az eredmény UNIX epoch ms formátumban.
    """
    # nap kiválasztása
    day_offset = random.randint(0, (END_DATE - START_DATE).days)
    day = START_DATE + timedelta(days=day_offset)

    # időablak: 14:00-tól másnap 01:30-ig
    window_start = day.replace(hour=14, minute=0, second=0, microsecond=0)
    window_end = (day + timedelta(days=1)).replace(hour=1, minute=30, second=0, microsecond=0)

    total_minutes = int((window_end - window_start).total_seconds() // 60)

    # válasszunk egy 15 perces slotot, kis zajjal
    slot_index = random.randint(0, total_minutes // 15)
    base_minute = slot_index * 15
    jitter = random.randint(-2, 2)
    minute_offset = max(0, min(total_minutes, base_minute + jitter))
    second_offset = random.randint(0, 59)

    dt = window_start + timedelta(minutes=minute_offset, seconds=second_offset)
    return int(dt.timestamp() * 1000)  # UNIX epoch ms


def generate_race_data(n: int) -> List[Race_Data]:
    RDS: List[Race_Data] = []
    with open("data/raw/cars.json", "r", encoding="utf-8") as f:
        cars = json.load(f)
    with open("data/raw/tracks.json", "r", encoding="utf-8") as f:
        tracks = json.load(f)

    used_ids = set()

    for _ in range(n):
        # race_id generálás
        chars = string.ascii_letters + string.digits
        race_id = ''.join(random.choice(chars) for _ in range(6))
        while race_id in used_ids:
            race_id = ''.join(random.choice(chars) for _ in range(6))
        used_ids.add(race_id)

        car_class = random.choice(list(cars.keys()))
        track = random.choice(list(tracks.keys()))
        layout = random.choice(tracks[track])["layout"]

        timestamp = _random_start_time()

        RDS.append(Race_Data(race_id, track, layout, car_class, timestamp))

    return RDS
