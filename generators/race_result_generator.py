import json
import random
from pathlib import Path
from typing import List, Dict, Any
from data.basic.model_classes import Race_Data, Player

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

def _get_best_lap_ms(reference_laps: Dict[str, Any], rd: Race_Data) -> int:
    layout_data = reference_laps[rd.track][rd.layout]
    classes = layout_data["car_class"]
    times = layout_data["best_lap_ms"]
    idx = classes.index(rd.car_class)
    return times[idx]

def _generate_player_laps(
    best_lap_ms: int,
    player: Player,
    n_laps: int,
    incidents_data: Dict[str, Dict[str, int]]
) -> Dict[str, Any]:
    laps = []
    incident_points_total = 0

    for lap_index in range(n_laps):
        # teljesítmény effektek
        rep_effect = 1 + ((100 - player.reputation) / 2000)
        rating_effect = 1 - ((player.elo_rating - 1500) / 10000)
        craft_effect = 1 + (random.uniform(-0.02, 0.02) / (player.race_count + 1))
        luck = random.uniform(0.95, 1.05)

        base = best_lap_ms
        if lap_index == 0:
            base = int(base * 1.10)

        laptime = int(base * rep_effect * rating_effect * craft_effect * luck)

        lap_incidents = []
        incident_count = random.choices([0, 1, 2], weights=[70, 25, 5], k=1)[0]
        for _ in range(incident_count):
            candidates = list(incidents_data.keys())
            if lap_index > 0 and "False Start" in candidates:
                candidates.remove("False Start")
            if not candidates:
                break
            inc = random.choice(candidates)
            lap_incidents.append(inc)
            incident_points_total += incidents_data[inc]["points"]

        valid = not any(inc == "Track Limit" for inc in lap_incidents)

        laps.append({
            "lap": lap_index + 1,
            "time": laptime,
            "valid": valid,
            "position": None,
            "incidents": lap_incidents
        })

    total_time = sum(l["time"] for l in laps)
    return {"laps": laps, "incident_points_total": incident_points_total, "total_time": total_time}

def _update_ratings(participants: List[Dict[str, Any]], K: int = 32):
    for i, p in enumerate(participants):
        rating_before = p["results"]["rating_before"]
        rating_change = 0
        for j, opp in enumerate(participants):
            if i == j:
                continue
            opp_rating = opp["results"]["rating_before"]
            expected = 1 / (1 + 10 ** ((opp_rating - rating_before) / 400))
            if p["total_time"] < opp["total_time"]:
                actual = 1
            elif p["total_time"] > opp["total_time"]:
                actual = 0
            else:
                actual = 0.5
            rating_change += K * (actual - expected)
        rating_change /= (len(participants) - 1)
        p["results"]["rating_change"] = round(rating_change, 3)
        new_rating = rating_before + rating_change
        p["new_rating"] = max(1000, min(2500, round(new_rating, 3)))

def _update_reputation(participants: List[Dict[str, Any]]):
    for p in participants:
        rep_before = p["results"]["reputation_before"]
        rep_change = 0.0

        # incidensek büntetése (enyhébb, mint eddig)
        if p["incident_points"] > 0:
            rep_change += round(-0.2 * p["incident_points"], 3)

        # tiszta körök jutalmazása (erősebb, mint eddig)
        clean_laps = sum(1 for lap in p["laps"] if lap["valid"])
        rep_change += round(clean_laps * 0.05, 3)

        # teljesen tiszta verseny extra jutalom
        if p["incident_points"] == 0:
            rep_change += 5.0

        # kis random faktor, hogy ne legyen túl steril
        rep_change += round(random.uniform(-1.0, 2.0), 3)

        p["results"]["reputation_change"] = rep_change
        new_rep = rep_before + rep_change

        # biztosítsuk, hogy a reputáció 50–100 között mozogjon a legtöbbször
        if new_rep < 50:
            # húzzuk fel egy kicsit
            new_rep = 50 + random.uniform(0, 10)

        p["new_rep"] = max(0.0, min(100.0, round(new_rep, 3)))


def generate_laps(
    rd: Race_Data,
    players_selected: List[Player],
    min_laps: int = 8,
    max_laps: int = 18
) -> Dict[str, Any]:
    with open(DATA_DIR / "reference_laps.json", "r", encoding="utf-8") as f:
        reference_laps = json.load(f)
    with open(DATA_DIR / "incidents.json", "r", encoding="utf-8") as f:
        incidents_data = json.load(f)

    best_lap_ms = _get_best_lap_ms(reference_laps, rd)
    n_laps = random.randint(min_laps, max_laps)

    random.shuffle(players_selected)

    participants = []
    for start_pos, p in enumerate(players_selected, start=1):
        laps_pack = _generate_player_laps(best_lap_ms, p, n_laps, incidents_data)

        rating_before = p.elo_rating
        rep_before = p.reputation

        participants.append({
            "user_id": p.USER_ID,
            "username": getattr(p, "username", f"Player{p.USER_ID}"),
            "start_position": start_pos,
            "finish_position": None,
            "incident_points": laps_pack["incident_points_total"],
            "total_time": laps_pack["total_time"],
            "results": {
                "rating_before": round(rating_before, 3),
                "reputation_before": round(rep_before, 3),
                "rating_change": 0.0,
                "reputation_change": 0.0
            },
            "laps": laps_pack["laps"]
        })

    participants.sort(key=lambda x: x["total_time"])
    for final_pos, part in enumerate(participants, start=1):
        part["finish_position"] = final_pos
        for lap in part["laps"]:
            lap["position"] = final_pos

    _update_ratings(participants)
    _update_reputation(participants)

    for part in participants:
        player = next(p for p in players_selected if p.USER_ID == part["user_id"])
        player.elo_rating = part["new_rating"]
        player.reputation = part["new_rep"]
        player.race_count += 1

    race_json = {
        "race_id": rd.RACE_ID,
        "track": rd.track,
        "layout": rd.layout,
        "car_class": rd.car_class,
        "participants": participants
    }
    return race_json