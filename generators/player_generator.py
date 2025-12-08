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

        fn, ln = fake.first_name(), fake.last_name()
        full_name = f"{fn} {ln}"

        username_suffix = [str(random.randint(0, 99)) for _ in range(90)] \
                          + ["33","44"]*2 \
                          + ["the_goat", "max", "professor", "PR0F3SS0R", "PR0F", "KedvesPalacsinta"]*8
        username = f"{random.choice([fn, ln])}_{random.choice(username_suffix)}"

        team_suffix = random.choice(["SIM RACING", "ESPORT", "RACING"])
        team_name = random.choice([fn, ln, country])
        team = random.choice(
            ["PRIVATEER"]*50 +
            [f"{team_name.upper()} {team_suffix}"]*30 +
            [f"TEAM {team_name.upper()}"]*20
        )

        user_id = random.randint(10000000, 99999999)
        while user_id in used_ids:
            user_id = random.randint(10000000, 99999999)
        used_ids.add(user_id)

        player = Player(user_id, username, full_name, country, team)
        players.append(player)

    return players