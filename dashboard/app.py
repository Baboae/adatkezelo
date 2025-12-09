import streamlit as st
import pandas as pd
from pathlib import Path
import json

from functions.unix_to_datetime import unix_to_datetime

# Plotly optional
use_plotly = True
try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    use_plotly = False

# --- Paths ---
BASE_JSON = Path(__file__).resolve().parent.parent / "created" / "jsons"
RESULTS_DIR = BASE_JSON / "race_results"

# --- Load data ---
players_df = pd.read_json(BASE_JSON / "players.json")
races_df = pd.read_json(BASE_JSON / "race_meta.json")

# Flatten race_results
rows = []
race_files = sorted(RESULTS_DIR.glob("*.json"))
for order, f in enumerate(race_files, start=1):
    try:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            for race in data:
                race_id = race.get("race_id")
                date = race.get("timestamp")
                track = race.get("track")
                layout = race.get("layout")
                car_class = race.get("car_class")
                for p in race.get("participants", []):
                    rows.append({
                        "race_id": race_id,
                        "Date": unix_to_datetime(date),
                        "timestamp": date,
                        "race_order": order,
                        "track": track,
                        "layout": layout,
                        "car_class": car_class,
                        "username": p.get("username"),
                        "start_position": p.get("start_position"),
                        "finish_position": p.get("finish_position"),
                        "incident_points": p.get("incident_points"),
                        "total_time": p.get("total_time"),
                        "new_rating": p.get("new_rating"),
                        "new_rep": p.get("new_rep"),
                    })
    except Exception:
        continue

participations_df = pd.DataFrame(rows)

st.set_page_config(page_title="Race History App", layout="wide")
st.title("Race History App")

# --- Session state ---
if "view" not in st.session_state:
    st.session_state.view = "lb"
if "selected_username" not in st.session_state:
    st.session_state.selected_username = None
if "selected_race_id" not in st.session_state:
    st.session_state.selected_race_id = None

# --- Leaderboard view ---
if st.session_state.view == "lb":
    st.header("Global leaderboard")

    lb_cols = ["username", "full_name", "elo_rating", "reputation", "race_count"]
    lb_df = players_df[lb_cols].sort_values(
        by=["elo_rating", "reputation"], ascending=[False, False]
    ).reset_index(drop=True)

    st.dataframe(lb_df)

    selected_username = st.selectbox("Select a player:", lb_df["username"])
    if st.button("View career"):
        st.session_state.selected_username = selected_username
        st.session_state.view = "player"
        st.session_state.selected_race_id = None

# --- Player career view ---
else:
    if st.button("⬅️ Back"):
        st.session_state.view = "lb"
        st.session_state.selected_username = None
        st.session_state.selected_race_id = None

    selected_username = st.session_state.selected_username
    if not selected_username or participations_df.empty:
        st.info("No race participations found.")
    else:
        st.subheader(f"Career — {selected_username}")
        player_df = participations_df.loc[
            participations_df["username"] == selected_username
        ].sort_values(["race_order", "timestamp"]).reset_index(drop=True)

        num_races = len(player_df)
        if num_races < 20:
            st.warning("Not enough data (<20 races). Trends may be misleading.")
        elif num_races < 50:
            st.info("Statistics are based on limited data (20–50 races). Interpret with caution.")
        else:
            st.success("Sufficient data (>50 races). Statistics are reliable.")

        st.markdown("#### Race history")
        rh_cols = ["race_order","Date","race_id","track","layout","car_class",
                   "start_position","finish_position","incident_points","total_time",
                   "new_rating","new_rep"]
        st.dataframe(player_df[rh_cols])

        selected_race_id = st.selectbox("Select a race:", player_df["race_id"].unique())
        if st.button("Show laps"):
            st.session_state.selected_race_id = selected_race_id

        if st.session_state.selected_race_id:
            st.markdown("#### Laps")
            laps_rows = []
            race_file = RESULTS_DIR / f"{st.session_state.selected_race_id}.json"
            try:
                with open(race_file, "r", encoding="utf-8") as fh:
                    race_data = json.load(fh)[0]
                    for p in race_data.get("participants", []):
                        if p.get("username") == selected_username:
                            for l in p.get("laps", []):
                                laps_rows.append({
                                    "lap": l.get("lap"),
                                    "time": l.get("time"),
                                    "position": l.get("position"),
                                    "valid": l.get("valid"),
                                    "incidents": ", ".join(l.get("incidents") or []),
                                })
                laps_df = pd.DataFrame(laps_rows)
                st.dataframe(laps_df)
            except Exception:
                st.info("No laps data available.")