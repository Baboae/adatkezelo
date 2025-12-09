import subprocess
import random
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

from data.basic.model_classes import Player, Race_Data, RaceResult
from functions.unix_to_datetime import unix_to_datetime
from functions.unix_to_ts import unix_to_timestamp
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_result_generator import generate_laps, _get_best_lap_ms

from functions.json_io import save_json
from functions.csv_io import save_csv
from functions.xlsx_io import save_xlsx
from functions.clear_results import clear_results
from functions.sql_handler import SQLHandler

import json

DATA_DIR = Path(__file__).parent / "data" / "raw"


def estimate_race_duration_ms(rd: Race_Data) -> int:
    """Becsült versenyidő a referencia köridő alapján."""
    with open(DATA_DIR / "reference_laps.json", "r", encoding="utf-8") as f:
        reference_laps = json.load(f)
    best_lap_ms = _get_best_lap_ms(reference_laps, rd)
    # 1. kör 1.10x, többi 1.05x, átlagosan 8 kör
    estimated_laps = 8
    total = int(best_lap_ms * 1.10) + int(best_lap_ms * 1.05) * (estimated_laps - 1)
    return total


def main():
    clear_results()
    Path("race_results").mkdir(parents=True, exist_ok=True)

    PLAYERS: List[Player] = generate_players(32)
    RACES: List[Race_Data] = generate_race_data(160)
    race_results: List[RaceResult] = []

    # játékosok utolsó elérhetősége
    last_available: Dict[int, int] = {p.USER_ID: 0 for p in PLAYERS}

    # idő szerint rendezett versenyek
    RACES.sort(key=lambda r: r.timestamp)

    for rd in RACES:
        start_ts = rd.timestamp
        est_duration = estimate_race_duration_ms(rd)
        end_ts = start_ts + est_duration

        # szabad játékosok
        available = [p for p in PLAYERS if last_available[p.USER_ID] <= start_ts]
        if len(available) < 3:
            continue  # kihagyjuk, ha nincs elég szabad játékos

        num_participants = min(3, len(available))
        participants = random.sample(available, num_participants)

        rr: RaceResult = generate_laps(rd, participants, min_laps=3, max_laps=10)
        race_results.append(rr)

        # frissítjük a játékosok elérhetőségét
        for p in participants:
            last_available[p.USER_ID] = end_ts

        # per-race export
        save_json([rr], f"race_results/{rr.race_id}.json")
        save_csv([rr], f"race_results/{rr.race_id}.csv")

        race_meta = [{
            "race_id": rr.race_id,
            "track": rr.track,
            "layout": rr.layout,
            "car_class": rr.car_class,
            "timestamp": unix_to_datetime(rr.timestamp)
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
                "total_time": unix_to_timestamp(p.total_time),
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
                    "time": unix_to_timestamp(l.time),
                    "position": l.position,
                    "valid": l.valid,
                    "incidents": ", ".join(l.incidents) if l.incidents else ""
                })

        save_xlsx({
            "RaceResult": race_meta,
            "Participants": participants_rows,
            "Laps": laps_rows
        }, f"race_results/{rr.race_id}.xlsx")

    # global exports
    save_json(PLAYERS, "players.json")
    save_json(RACES, "race_meta.json")
    save_csv(PLAYERS, "players.csv")
    save_csv(RACES, "race_meta.csv")
    save_xlsx({"Players": PLAYERS}, "players.xlsx")
    save_xlsx({"Races": RACES}, "race_meta.xlsx")

    # DB betöltés (opcionális)
    loaddb = False
    if loaddb:
        handler = SQLHandler()
        handler.connect()
        handler.clear_tables()
        handler.create_schema()
        handler.insert_players(PLAYERS)
        handler.insert_races(RACES)
        handler.insert_results(race_results)
        handler.commit()

        handler.cur.execute("SELECT COUNT(*) FROM players")
        print("Betöltött játékosok száma:", handler.cur.fetchone()[0])
        handler.cur.execute("SELECT COUNT(*) FROM races")
        print("Betöltött versenyek száma:", handler.cur.fetchone()[0])

        handler.close()

    subprocess.run(["python", "-m", "streamlit", "run", "dashboard/app.py"])


if __name__ == "__main__":
    main()