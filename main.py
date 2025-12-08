import random
import os
from pathlib import Path
from typing import List
from data.basic.model_classes import Player, Race_Data
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_lap_generator import generate_laps
from functions.save_to_json import save_list_to_json

def main():
    # --- race_results mappa ürítése ---
    results_dir = Path("created/race_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    for file in results_dir.iterdir():
        if file.is_file():
            file.unlink()

    # játékosok és versenyek
    PLAYERS: List[Player] = generate_players(32)
    RACES: List[Race_Data] = generate_race_data(53)

    race_jsons = []

    for rd in RACES:
        num_participants = random.randint(5, 12)
        participants = random.sample(PLAYERS, num_participants)

        race_dict = generate_laps(rd, participants, min_laps=8, max_laps=18)
        race_jsons.append(race_dict)

        save_list_to_json([race_dict], f"race_results/{race_dict['race_id']}.json")

    # frissített játékosok mentése
    save_list_to_json(PLAYERS, "players.json")

    # verseny metaadatok mentése
    save_list_to_json(RACES, "race_meta.json")

if __name__ == "__main__":
    main()
