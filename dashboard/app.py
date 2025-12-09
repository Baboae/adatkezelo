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

# AgGrid
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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

# --- Helper: normalize selected_rows ---
def normalize_selected_rows(resp):
    rows = resp.get("selected_rows", [])
    if isinstance(rows, pd.DataFrame):
        rows = rows.to_dict("records")
    return rows if isinstance(rows, list) else []

# --- Leaderboard view ---
if st.session_state.view == "lb":
    st.header("Global leaderboard")

    lb_cols = ["username", "full_name", "elo_rating", "reputation", "race_count"]
    lb_df = players_df[lb_cols].sort_values(
        by=["elo_rating", "reputation"], ascending=[False, False]
    ).reset_index(drop=True)

    gb = GridOptionsBuilder.from_dataframe(lb_df)
    gb.configure_selection("single", use_checkbox=False)
    gb.configure_grid_options(rowSelection="single", suppressRowClickSelection=False)
    grid_resp = AgGrid(lb_df, gridOptions=gb.build(),
                       update_mode=GridUpdateMode.SELECTION_CHANGED,
                       height=500, fit_columns_on_grid_load=True)

    selected_rows = normalize_selected_rows(grid_resp)
    if selected_rows:
        st.session_state.selected_username = selected_rows[0]["username"]
        st.session_state.view = "player"
        st.session_state.selected_race_id = None
        st.experimental_rerun()

# --- Player career view ---
else:
    if st.button("⬅️ Back"):
        st.session_state.view = "lb"
        st.session_state.selected_username = None
        st.session_state.selected_race_id = None
        st.experimental_rerun()

    selected_username = st.session_state.selected_username
    if not selected_username or participations_df.empty:
        st.info("No race participations found.")
    else:
        st.subheader(f"Career — {selected_username}")
        player_df = participations_df.loc[
            participations_df["username"] == selected_username
        ].sort_values(["race_order", "timestamp"]).reset_index(drop=True)

        st.markdown("#### Race history")
        rh_cols = ["race_order","Date","race_id","track","layout","car_class",
                   "start_position","finish_position","incident_points","total_time",
                   "new_rating","new_rep"]
        gb_rh = GridOptionsBuilder.from_dataframe(player_df[rh_cols])
        gb_rh.configure_selection("single", use_checkbox=False)
        gb_rh.configure_grid_options(rowSelection="single", suppressRowClickSelection=False)
        grid_rh = AgGrid(player_df[rh_cols], gridOptions=gb_rh.build(),
                         update_mode=GridUpdateMode.SELECTION_CHANGED,
                         height=500, fit_columns_on_grid_load=True,
                         key=f"grid_rh_{selected_username}")

        selected_rows = normalize_selected_rows(grid_rh)
        if selected_rows:
            st.session_state.selected_race_id = selected_rows[0]["race_id"]

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
                gb_laps = GridOptionsBuilder.from_dataframe(laps_df)
                grid_laps = AgGrid(laps_df, gridOptions=gb_laps.build(),
                                   update_mode=GridUpdateMode.NO_UPDATE,
                                   height=300, fit_columns_on_grid_load=True,
                                   key=f"grid_laps_{st.session_state.selected_race_id}")
            except Exception:
                st.info("No laps data available.")