import streamlit as st
import pandas as pd
from pathlib import Path
import json
import logging
import uuid

from functions.unix_to_ts import unix_to_timestamp
from functions.unix_to_datetime import unix_to_datetime

# Optional Plotly
use_plotly = True
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    use_plotly = False

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

logging.basicConfig(level=logging.INFO)

# --- Paths ---
BASE_JSON = Path(__file__).resolve().parent.parent / "created" / "jsons"
RESULTS_DIR = BASE_JSON / "race_results"


# --- Caching ---
@st.cache_data
def load_players():
    try:
        df = pd.read_json(BASE_JSON / "players.json")
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        logging.error(f"Failed to load players.json: {e}")
        return pd.DataFrame()


@st.cache_data
def load_participations():
    rows = []
    if not RESULTS_DIR.exists():
        return pd.DataFrame()

    race_files = sorted(RESULTS_DIR.glob("*.json"))
    logging.info(f"Found {len(race_files)} race files")

    for order, f in enumerate(race_files, start=1):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if not isinstance(data, list) or not data:
                    continue

                race = data[0]
                race_id = race.get("race_id", f.stem)
                date = race.get("timestamp", 0)
                track = race.get("track", "Unknown")
                layout = race.get("layout", "")
                car_class = race.get("car_class", "")

                participants = race.get("participants", [])

                for p in participants:
                    row = {
                        "race_id": race_id,
                        "Date": unix_to_datetime(date),
                        "timestamp": date,
                        "race_order": order,
                        "track": track,
                        "layout": layout,
                        "car_class": car_class,
                        "username": p.get("username", ""),
                        "start_position": p.get("start_position", 0),
                        "finish_position": p.get("finish_position", 0),
                        "incident_points": p.get("incident_points", 0),
                        "total_time": p.get("total_time", ""),
                        "new_rating": p.get("new_rating", 0),
                        "new_rep": p.get("new_rep", 0),
                    }
                    rows.append(row)
        except Exception as e:
            logging.warning(f"Failed to load {f.name}: {e}")

    df = pd.DataFrame(rows)
    logging.info(
        f"Loaded {len(df)} participation rows for {df['username'].nunique() if not df.empty else 0} unique players")
    return df


# Load data
players_df = load_players()
participations_df = load_participations()

st.set_page_config(page_title="Race History App", layout="wide")
st.title("Race History Dashboard 🏁🏎️")

# --- Session State ---
if "view" not in st.session_state:
    st.session_state.view = "lb"
if "selected_username" not in st.session_state:
    st.session_state.selected_username = None
if "selected_race_id" not in st.session_state:
    st.session_state.selected_race_id = None


# --- Helper functions ---
def normalize_selected_rows(grid_resp):
    """Convert AgGrid response to list of dicts"""
    if grid_resp is None:
        return []

    selected = grid_resp.get("selected_rows", [])

    # Handle DataFrame case
    if isinstance(selected, pd.DataFrame):
        selected = selected.to_dict("records")

    # Handle single row case
    if isinstance(selected, dict):
        selected = [selected]

    # Ensure it's a list
    if not isinstance(selected, list):
        selected = []

    return selected


def safe_aggrid(df, height=400, key=None, selectable=True):
    """Safe AgGrid wrapper"""
    if df.empty:
        st.info("No data available.")
        return {"selected_rows": []}

    try:
        gb = GridOptionsBuilder.from_dataframe(df)
        if selectable:
            gb.configure_selection("single", use_checkbox=False, header_checkbox=False)
            gb.configure_grid_options(
                rowSelection="single",
                suppressRowClickSelection=False,
                suppressRowDeselection=True
            )

        grid_options = gb.build()
        grid_resp = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED if selectable else GridUpdateMode.NO_UPDATE,
            height=height,
            fit_columns_on_grid_load=True,
            key=key or f"grid_{uuid.uuid4()}",
            allow_unsafe_jscode=False
        )
        return grid_resp
    except Exception as e:
        st.error(f"Table error: {e}")
        logging.error(f"AgGrid error: {e}")
        return {"selected_rows": []}


def get_player_races(username):
    if participations_df.empty:
        return pd.DataFrame()
    player_mask = participations_df['username'] == username
    if not player_mask.any():
        return pd.DataFrame()
    return participations_df[player_mask].copy()


# --- MAIN VIEWS ---
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("## Navigation")
    if st.button("Leaderboard", key="nav_lb"):
        st.session_state.view = "lb"
        st.session_state.selected_username = None
        st.session_state.selected_race_id = None
        st.rerun()

    if st.session_state.view != "lb" and st.session_state.selected_username:
        st.success(f"👤 {st.session_state.selected_username}")

with col2:
    # Leaderboard View
    if st.session_state.view == "lb":
        st.header("🏆 Global Leaderboard 🏆")

        if players_df.empty:
            st.warning("No player data found. ❌")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Players", len(players_df))
            # JAVÍTOTT: Egyedi race-ek száma (nem participants)
            unique_races = len(participations_df['race_id'].unique()) if not participations_df.empty else 0
            with col_b:
                st.metric("Total Races", unique_races)

            lb_cols = ["username", "full_name", "elo_rating", "reputation", "race_count"]
            available_cols = [col for col in lb_cols if col in players_df.columns]
            lb_df = players_df[available_cols].sort_values(
                by=["elo_rating", "reputation"], ascending=[False, False], na_position='last'
            ).head(100).reset_index(drop=True)

            grid_resp = safe_aggrid(lb_df, height=500, selectable=True, key="leaderboard_grid")

            selected_rows = normalize_selected_rows(grid_resp)
            if len(selected_rows) > 0:
                st.session_state.selected_username = selected_rows[0].get("username")
                st.session_state.view = "player"
                st.rerun()

    # Player Career View
    elif st.session_state.selected_username:
        username = st.session_state.selected_username

        st.header(f"👤 {username}'s Career")

        player_races = get_player_races(username)

        if player_races.empty:
            st.warning(f"❌ No race data found for {username}")
        else:
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Total Races", len(player_races))
            with col_stats2:
                avg_finish = player_races['finish_position'].mean()
                st.metric("Avg Finish Pos", f"{avg_finish:.1f}" if not pd.isna(avg_finish) else "N/A")
            with col_stats3:
                total_incidents = player_races['incident_points'].sum()
                st.metric("Total Incidents", total_incidents)

            st.subheader("📋 Race History")
            # JAVÍTOTT: race_order eltávolítva a táblázatból
            rh_cols = ["Date", "race_id", "track", "start_position",
                       "finish_position", "incident_points", "new_rating", "new_rep"]
            rh_df = player_races[rh_cols].sort_values(["Date"], ascending=False)

            grid_rh_resp = safe_aggrid(rh_df, height=400, selectable=True, key=f"player_races_{username}")

            selected_race_rows = normalize_selected_rows(grid_rh_resp)
            if len(selected_race_rows) > 0:
                st.session_state.selected_race_id = selected_race_rows[0].get("race_id")

            # Laps detail
            if st.session_state.selected_race_id:
                st.subheader("⏱️ Lap Details")
                race_file = RESULTS_DIR / f"{st.session_state.selected_race_id}.json"

                if race_file.exists():
                    try:
                        with open(race_file, "r", encoding="utf-8") as f:
                            race_data = json.load(f)[0]

                        laps_data = []
                        for participant in race_data.get("participants", []):
                            if participant.get("username") == username:
                                for lap in participant.get("laps", []):
                                    lap_time = unix_to_timestamp(lap.get("time", 0))
                                    laps_data.append({
                                        "lap": lap.get("lap", 0),
                                        "time": lap_time,
                                        "position": lap.get("position", ""),
                                        "valid": lap.get("valid", False),
                                        "incidents": ", ".join(lap.get("incidents", []))
                                    })

                        if laps_data:
                            laps_df = pd.DataFrame(laps_data)
                            safe_aggrid(laps_df, height=250, selectable=False,
                                        key=f"laps_{st.session_state.selected_race_id}")
                        else:
                            st.info("No lap data available.")

                    except Exception as e:
                        st.error(f"Error loading race data: {e}")
                else:
                    st.warning(f"Race file not found: {race_file}")

        if st.button("🔙 Back to Leaderboard", key="back_btn"):
            st.session_state.view = "lb"
            st.rerun()