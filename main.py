import random
from pathlib import Path
from typing import List

from data.basic.model_classes import Player, Race_Data, RaceResult
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_result_generator import generate_laps

from functions.json_io import save_json
from functions.csv_io import save_csv
from functions.xlsx_io import save_xlsx
from functions.clear_results import clear_results
from functions.unix_to_ts import unix_to_timestamp  # ha debughoz időket formáznál
from functions.sql_handler import SQLHandler


def main():
    # 0) ensure race_results folder is clean and exists
    clear_results()
    Path("race_results").mkdir(parents=True, exist_ok=True)

    # 1) generate data
    PLAYERS: List[Player] = generate_players(3)
    RACES: List[Race_Data] = generate_race_data(3)  # növelhető ha stabil
    race_results: List[RaceResult] = []

    for rd in RACES:
        num_participants = random.randint(3, 3)
        participants = random.sample(PLAYERS, num_participants)
        rr: RaceResult = generate_laps(rd, participants, min_laps=3, max_laps=3)
        race_results.append(rr)

        # per-race exports into race_results/{race_id}.ext
        save_json([rr], f"race_results/{rr.race_id}.json")
        save_csv([rr], f"race_results/{rr.race_id}.csv")

        # Excel: three sheets per race file
        race_meta = [{
            "race_id": rr.race_id,
            "track": rr.track,
            "layout": rr.layout,
            "car_class": rr.car_class
        }]
        participants_rows = []
        for p in rr.participants:
            participants_rows.append({
                "race_id": rr.race_id,
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
        laps_rows = []
        for p in rr.participants:
            for l in p.laps:
                laps_rows.append({
                    "race_id": rr.race_id,
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
        }, f"race_results/{rr.race_id}.xlsx")

    # global exports for convenience
    save_json(PLAYERS, "players.json")
    save_json(RACES, "race_meta.json")
    save_csv(PLAYERS, "players.csv")
    save_csv(RACES, "race_meta.csv")
    save_xlsx({"Players": PLAYERS}, "players.xlsx")
    save_xlsx({"Races": RACES}, "race_meta.xlsx")

    # 2) DB load via handler
    loaddb = True  # állítsd True-ra ha tölteni akarsz DB-be
    if loaddb:
        handler = SQLHandler()
        handler.connect()
        handler.create_schema()
        handler.clear_tables()
        handler.insert_players(PLAYERS)
        handler.insert_races(RACES)
        handler.insert_results(race_results)
        handler.commit()

        # 3) quick checks
        handler.cur.execute("SELECT COUNT(*) FROM players")
        print("Betöltött játékosok száma:", handler.cur.fetchone()[0])
        handler.cur.execute("SELECT COUNT(*) FROM races")
        print("Betöltött versenyek száma:", handler.cur.fetchone()[0])

        handler.close()


if __name__ == "__main__":
    main()