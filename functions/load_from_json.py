import json
from typing import List, Any, Type, TypeVar
from dataclasses import asdict, is_dataclass
from pathlib import Path

T = TypeVar("T")

def load_from_json(filename: str, cls: Type[T]) -> List[T]:
    """
    Load a list of objects from a JSON file and convert them into dataclass instances.

    Args:
        filename (str): Path to the JSON file to load (relative to 'created/' mappa).
        cls (Type[T]): The dataclass type to instantiate (pl. Player, Race_Data).

    Returns:
        List[T]: A list of dataclass instances.
    """
    path = Path("created") / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result: List[T] = []
    for item in data:
        if is_dataclass(cls):
            result.append(cls(**item))
        else:
            result.append(item)
    return result