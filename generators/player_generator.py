#generators/player_generator.py:

import json
import random
from typing import List
from pathlib import Path
from faker import Faker
from data.basic.model_classes import Player

def generate_players(n: int) -> List[Player]:
    DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
    with open(DATA_DIR / "locale_map.json", "r", encoding="utf-8") as f:
        countries = json.load(f)

    fakers = {c: Faker(locale=loc) for c, loc in countries.items()}
    players: List[Player] = []
    used_ids = set()

    for _ in range(n):
        country = random.choice(list(countries.keys()))
        fake = fakers[country]

        fn, ln = fake.first_name_male(), fake.last_name_male()
        full_name = f"{fn} {ln}"

        # alap suffixek
        base_suffixes = (
            [str(random.randint(0, 99)) for _ in range(50)]
            + ["33", "44"] * 2
            + ["the_goat", "max", "PR0F", "the_ApexHunter", "ChicaneKing", "Slipstreamer", "on_twitch", "twitch", "yt", "Cr1t1c4l", "HS", "b00st3d"]
        )

        # magyar specifikus nickek
        hungarian_suffixes = ["KedvesPalacsinta", "GamerHU", "HU", "hu", "Hu", "a_kuposzto", "a_vaci_ut_kiralya", "PEC"]

        if country == "Hungary":
            username_suffixes = base_suffixes + hungarian_suffixes * 5
        else:
            username_suffixes = base_suffixes

        username = f"{random.choice([fn, ln])}_{random.choice(username_suffixes)}"

        # team generálás
        team_suffixes = ["SIM RACING", "ESPORT", "RACING", "Motorsport", "Racing Team"]
        teamnames = ["TEAM REDLINE", "APEX HUNTERS", "Low Fuel Motorsport", "PetrolHead Simracing"]
        hungarian_teams = ["PEC", "GPSE", "SMC", "GTR-Masters"]
        team_name = random.choice([ln, fn, country])
        if country == "Hungary":
            team = random.choice(["PRIVATEER"]*40+[hungarian_teams]*45+[teamnames]*10+[f"TEAM {random.choice([fn, ln, country]).upper()}"])
        team = random.choice(
            ["PRIVATEER"] * 50
            + [random.choice(teamnames)] * 45
            + [f"TEAM {team_name.upper()}", f"{team_name.upper()} {random.choice(team_suffixes)}"] * 5
        )

        # egyedi user_id
        user_id = random.randint(10000000, 99999999)
        while user_id in used_ids:
            user_id = random.randint(10000000, 99999999)
        used_ids.add(user_id)

        player = Player(user_id, username, full_name, country, team)
        players.append(player)

    return players
