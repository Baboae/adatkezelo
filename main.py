import random
from pathlib import Path
from typing import List
from data.basic.model_classes import Player, Race_Data, RaceResult
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_result_generator import generate_laps
from functions.save_to_json import save_to_json
from functions.load_from_json import load_from_json

def main():
    # --- race_results mappa ürítése ---
    results_dir = Path("created/race_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    for file in results_dir.iterdir():
        if file.is_file():
            file.unlink()

    # játékosok és versenyek generálása
    PLAYERS: List[Player] = generate_players(100)
    RACES: List[Race_Data] = generate_race_data(3)

    race_results: List[RaceResult] = []

    for rd in RACES:
        num_participants = random.randint(3, 3)
        participants = random.sample(PLAYERS, num_participants)

        race_result: RaceResult = generate_laps(rd, participants, min_laps=8, max_laps=18)
        race_results.append(race_result)

        # mentés JSON-ba, dataclass → dict konverzió automatikusan megy
        save_to_json([race_result], f"race_results/{race_result.race_id}.json")

    # frissített játékosok mentése
    save_to_json(PLAYERS, "players.json")

    # verseny metaadatok mentése
    save_to_json(RACES, "race_meta.json")


    # Példa visszaolvasásra:
    players_loaded = load_from_json("players.json", Player)
    races_loaded = load_from_json("race_meta.json", Race_Data)

    print(f"Betöltött játékosok száma: {len(players_loaded)}")
    print(f"Betöltött versenyek száma: {len(races_loaded)}\n")

    for race in races_loaded:
        print(race.RACE_ID)
        results_loaded = load_from_json(f"race_results/{race.RACE_ID}.json", RaceResult)
        for result in results_loaded:
            print(f"{result.track}"
                  f"\n{result.layout}"
                  f"\n{result.car_class}\n")
            for p in result.participants:
                print(f"{p["username"]}"
                      f"\nStarted P{p["start_position"]}"
                      f"\nFinished P{p["finish_position"]}"
                      f"\nTime: {p["total_time"]}"
                      f"\n")
if __name__ == "__main__":
    main()
