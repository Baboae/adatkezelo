import json
import random
import string
from typing import List
from data.basic.model_classes import Race_Data

def generate_race_data(n: int) -> List[Race_Data]:
    RDS: List[Race_Data] = []
    with open("data/raw/cars.json", "r", encoding="utf-8") as f:
        cars = json.load(f)
    with open("data/raw/tracks.json", "r", encoding="utf-8") as f:
        tracks = json.load(f)

    used_ids = set()

    for _ in range(n):
        # --- race_id generálás közvetlenül itt ---
        chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
        race_id = ''.join(random.choice(chars) for _ in range(6))
        while race_id in used_ids:
            race_id = ''.join(random.choice(chars) for _ in range(6))
        used_ids.add(race_id)

        car_class = random.choice(list(cars.keys()))
        track = random.choice(list(tracks.keys()))
        layout = random.choice(tracks[track])["layout"]

        RDS.append(Race_Data(race_id, track, layout, car_class))

    return RDS
