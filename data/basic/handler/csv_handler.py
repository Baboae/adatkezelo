#functions/csv_handler.py:

import csv
from pathlib import Path
from dataclasses import asdict, is_dataclass
from typing import List, Type, TypeVar

T = TypeVar("T")

def save_csv(items: List, filename: str) -> None:
    path = Path("created/csvs/") / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(i) if is_dataclass(i) else i for i in items]
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            pass
        return
    headers = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

def load_csv(filename: str, cls: Type[T]) -> List[T]:
    path = Path("created/csvs/") / filename
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        items = []
        for row in r:
            for k, v in row.items():
                if v.isdigit():
                    row[k] = int(v)
            items.append(cls(**row))
    return items