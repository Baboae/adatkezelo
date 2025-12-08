import os
import random
import oracledb
from typing import List
from pathlib import Path
from dotenv import load_dotenv

from data.basic.model_classes import Player, Race_Data, RaceResult
from generators.player_generator import generate_players
from generators.race_data_generator import generate_race_data
from generators.race_result_generator import generate_laps

# export/load helpers — use the same ones as in your old main
from functions.json_io import save_json, load_from_json
from functions.csv_io import save_csv
from functions.xlsx_io import save_xlsx
from functions.clear_results import clear_results
from functions.unix_to_ts import unix_to_timestamp  # if you still print details

# --- .env ---
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE = os.getenv("DB_SERVICE")

def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        service_name=DB_SERVICE
    )

def clear_tables(cur):
    # order matters due to FKs
    for table in ["laps", "participants", "races", "players"]:
        cur.execute(f"TRUNCATE TABLE {table}")

def insert_players(cur, players: List[Player]):
    cur.executemany("""
        INSERT INTO players (user_id, username, rating, reputation)
        VALUES (:1, :2, :3, :4)
    """, [(p.USER_ID, p.username, p.elo_rating, p.reputation) for p in players])

def insert_races(cur, races: List[Race_Data]):
    cur.executemany("""
        INSERT INTO races (race_id, track, layout, car_class)
        VALUES (:1, :2, :3, :4)
    """, [(r.RACE_ID, r.track, r.layout, r.car_class) for r in races])

def insert_results(cur, race_results: List[RaceResult]):
    participants_rows = []
    laps_rows = []
    for result in race_results:
        for p in result.participants:
            participants_rows.append((
                result.race_id, p.user_id, p.start_position, p.finish_position,
                p.incident_points, p.total_time,
                p.results["rating_before"], p.results["rating_change"],
                p.results["reputation_before"], p.results["reputation_change"],
                p.new_rating, p.new_rep
            ))
            for l in p.laps:
                laps_rows.append((
                    result.race_id, p.user_id, l.lap, l.time,
                    l.position, "Y" if l.valid else "N",
                    ", ".join(l.incidents) if l.incidents else ""
                ))

    if participants_rows:
        cur.executemany("""
            INSERT INTO participants (
                race_id, user_id, start_position, finish_position,
                incident_points, total_time,
                rating_before, rating_change,
                reputation_before, reputation_change,
                new_rating, new_rep
            ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
        """, participants_rows)

    if laps_rows:
        cur.executemany("""
            INSERT INTO laps (
                race_id, user_id, lap, time, position, valid, incidents
            ) VALUES (:1,:2,:3,:4,:5,:6,:7)
        """, laps_rows)

def main():
    # 0) ensure race_results folder is clean and exists
    clear_results()
    Path("race_results").mkdir(parents=True, exist_ok=True)

    # 1) generate data
    PLAYERS: List[Player] = generate_players(32)
    RACES: List[Race_Data] = generate_race_data(100)  # increase once stable
    race_results: List[RaceResult] = []

    for rd in RACES:
        num_participants = random.randint(3, 22)
        participants = random.sample(PLAYERS, num_participants)
        rr: RaceResult = generate_laps(rd, participants, min_laps=3, max_laps=10)
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

    # 2) DB load
    conn = get_connection()
    cur = conn.cursor()
    clear_tables(cur)
    insert_players(cur, PLAYERS)
    insert_races(cur, RACES)
    insert_results(cur, race_results)
    conn.commit()

    # 3) quick checks
    cur.execute("SELECT COUNT(*) FROM players")
    print("Betöltött játékosok száma:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM races")
    print("Betöltött versenyek száma:", cur.fetchone()[0])

    conn.close()

if __name__ == "__main__":
    main()
