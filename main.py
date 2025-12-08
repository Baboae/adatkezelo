import random
from pathlib import Path
from typing import List
from data.basic.model_classes import Player, Race_Data, RaceResult
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_result_generator import generate_laps
from functions.json_io import save_to_json, load_from_json
from functions.csv_io import save_csv, load_csv
from functions.xlsx_io import save_xlsx, load_xlsx
from functions.unix_to_ts import unix_to_timestamp
from functions.clear_results import clear_results

def main():
    # --- race_results mappa ürítése ---
    clear_results()
    # játékosok és versenyek generálása
    PLAYERS: List[Player] = generate_players(32)
    RACES: List[Race_Data] = generate_race_data(100)

    race_results: List[RaceResult] = []

    for rd in RACES:
        num_participants = random.randint(3, 22)
        participants = random.sample(PLAYERS, num_participants)

        race_result: RaceResult = generate_laps(rd, participants, min_laps=3, max_laps=10)
        race_results.append(race_result)

        # JSON + CSV mentés
        save_to_json([race_result], f"race_results/{race_result.race_id}.json")
        save_csv([race_result], f"race_results/{race_result.race_id}.csv")

        # --- XLSX mentés: külön lapokon RaceResult, Participants, Laps ---
        # RaceResult metaadatok
        race_meta = [{
            "race_id": race_result.race_id,
            "track": race_result.track,
            "layout": race_result.layout,
            "car_class": race_result.car_class
        }]

        # Participants táblázat
        participants_rows = []
        for p in race_result.participants:
            participants_rows.append({
                "race_id": race_result.race_id,
                "user_id": p.user_id,
                "username": p.username,
                "start_position": p.start_position,
                "finish_position": p.finish_position,
                "incident_points": p.incident_points,
                "total_time": p.total_time,
                "rating_before": p.results["rating_before"],
                "rating_change": p.results["rating_change"],
                "reputation_before": p.results["reputation_before"],
                "reputation_change": p.results["reputation_change"],
                "new_rating": p.new_rating,
                "new_rep": p.new_rep
            })

        # Laps táblázat
        laps_rows = []
        for p in race_result.participants:
            for l in p.laps:
                laps_rows.append({
                    "race_id": race_result.race_id,
                    "user_id": p.user_id,
                    "lap": l.lap,
                    "time": l.time,
                    "position": l.position,
                    "valid": l.valid,
                    "incidents": ", ".join(l.incidents) if l.incidents else ""
                })

        save_xlsx({
            "RaceResult": race_meta,
            "Participants": participants_rows,
            "Laps": laps_rows
        }, f"race_results/{race_result.race_id}.xlsx")

    save_to_json(PLAYERS, "players.json")
    save_to_json(RACES, "race_meta.json")

    save_csv(PLAYERS,  "players.csv")
    save_csv(RACES, "race_meta.csv")

    save_xlsx({"Players": PLAYERS}, "players.xlsx")
    save_xlsx({"Races": RACES}, "race_meta.xlsx")

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
                      f"\nTime: {unix_to_timestamp(p["total_time"])}"
                      f"\nLaps:\n")
                for l in p["laps"]:
                    print(f"L{l["lap"]}, P{l["position"]}"
                          f"\nTime: {unix_to_timestamp(l['time'])}\n")
if __name__ == "__main__":
    main()
