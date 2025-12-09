import os
import oracledb
from dotenv import load_dotenv
from typing import List
from data.basic.model_classes import Player, Race_Data, RaceResult

# --- .env betöltése ---
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE = os.getenv("DB_SERVICE")


class SQLHandler:
    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self):
        self.conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            service_name=DB_SERVICE
        )
        self.cur = self.conn.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def clear_tables(self):
        for table in ["laps", "participants", "races", "players"]:
            try:
                self.cur.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
            except oracledb.DatabaseError:
                pass
        self.conn.commit()

    def create_schema(self):
        """
        Új táblák létrehozása a dataclass-okhoz illeszkedve.
        """
        tables_sql = {
            "players": """
                CREATE TABLE players (
                    user_id NUMBER PRIMARY KEY,
                    username VARCHAR2(100),
                    full_name VARCHAR2(200),
                    nationality VARCHAR2(100),
                    team VARCHAR2(200),
                    elo_rating FLOAT,
                    reputation FLOAT,
                    race_count NUMBER
                )
            """,
            "races": """
                CREATE TABLE races (
                    race_id VARCHAR2(20) PRIMARY KEY,
                    track VARCHAR2(200),
                    layout VARCHAR2(200),
                    car_class VARCHAR2(100)
                )
            """,
            "participants": """
                CREATE TABLE participants (
                    race_id VARCHAR2(20) REFERENCES races(race_id),
                    user_id NUMBER REFERENCES players(user_id),
                    start_position NUMBER,
                    finish_position NUMBER,
                    incident_points NUMBER,
                    total_time NUMBER,
                    rating_before FLOAT,
                    rating_change FLOAT,
                    reputation_before FLOAT,
                    reputation_change FLOAT,
                    new_rating FLOAT,
                    new_rep FLOAT,
                    PRIMARY KEY (race_id, user_id)
                )
            """,
            "laps": """
                CREATE TABLE laps (
                    race_id VARCHAR2(20) REFERENCES races(race_id),
                    user_id NUMBER REFERENCES players(user_id),
                    lap NUMBER,
                    time NUMBER,
                    position NUMBER,
                    valid CHAR(1),
                    incidents VARCHAR2(500),
                    PRIMARY KEY (race_id, user_id, lap)
                )
            """
        }

        for name, sql in tables_sql.items():
            try:
                self.cur.execute(sql)
            except oracledb.DatabaseError as e:
                if "ORA-00955" in str(e):  # name already used
                    pass
                else:
                    raise

        self.conn.commit()

    def insert_players(self, players: List[Player]):
        self.cur.executemany("""
            INSERT INTO players (user_id, username, full_name, nationality, team, elo_rating, reputation, race_count)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
        """, [(p.USER_ID, p.username, p.full_name, p.nationality, p.team, p.elo_rating, p.reputation, p.race_count) for p in players])

    def insert_races(self, races: List[Race_Data]):
        self.cur.executemany("""
            INSERT INTO races (race_id, track, layout, car_class)
            VALUES (:1,:2,:3,:4)
        """, [(r.RACE_ID, r.track, r.layout, r.car_class) for r in races])

    def insert_results(self, race_results: List[RaceResult]):
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
            self.cur.executemany("""
                INSERT INTO participants (
                    race_id, user_id, start_position, finish_position,
                    incident_points, total_time,
                    rating_before, rating_change,
                    reputation_before, reputation_change,
                    new_rating, new_rep
                ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
            """, participants_rows)

        if laps_rows:
            self.cur.executemany("""
                INSERT INTO laps (
                    race_id, user_id, lap, time, position, valid, incidents
                ) VALUES (:1,:2,:3,:4,:5,:6,:7)
            """, laps_rows)

    def commit(self):
        self.conn.commit()
