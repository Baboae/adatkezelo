import json
import random
from typing import List
from pathlib import Path
from data.basic.model_classes import Race_Laps, Player, Race_Data

def generate_race_laps(players: List[Player], race: Race_Data, laps_per_player: int) -> List[Race_Laps]:
    DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
    with open(DATA_DIR / "reference_laps.json", "r", encoding="utf-8") as f:
        ref_laps = json.load(f)

    # referencia idő adott pálya + layout + car_class
    base_time = None
    if race.track in ref_laps and race.layout in ref_laps[race.track]:
        layout_data = ref_laps[race.track][race.layout]
        if race.car_class in layout_data["car_class"]:
            idx = layout_data["car_class"].index(race.car_class)
            base_time = layout_data["best_lap_ms"][idx]

    if base_time is None:
        # fallback: ha nincs referencia, random 60-120 másodperc
        base_time = random.randint(60000, 120000)

    laps: List[Race_Laps] = []
    for p in players:
        for lap_index in range(laps_per_player):
            skill_factor = (p.elo_rating - 1500) / 1500
            variation = random.uniform(-0.05, 0.05)
            lap_time = int(base_time * (1 + variation - 0.03 * skill_factor))

            # első kör lassabb
            if lap_index == 0:
                lap_time += random.randint(8000, 12000)  # +8–12 másodperc

            laps.append(Race_Laps(race.RACE_ID, p.USER_ID, lap_time))

    return laps
