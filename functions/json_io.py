#functions/json_io.py:

import json
from pathlib import Path
from data.basic.model_classes import *
from dataclasses import asdict, is_dataclass
from typing import List, Any, Type, TypeVar

T = TypeVar("T")

def save_json(items: List[Any], filename: str) -> None:
    """
    Save any list of objects into a JSON file.
    Handles dataclasses, dicts, and primitive types.

    Args:
        items (List[Any]): List of objects (dataclass, dict, str, int, etc.)
        filename (str): Path to the JSON file to save.
    """
    serialized = []
    for item in items:
        if is_dataclass(item):
            serialized.append(asdict(item))
        elif isinstance(item, (dict, list, str, int, float, bool, type(None))):
            serialized.append(item)
        else:
            # Fallback: try to convert to string
            serialized.append(str(item))

    with open(f"created/jsons/{filename}", "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=4, ensure_ascii=False)

def load_from_json(filename: str, cls: Type[T]) -> List[T]:
    """
    Load a list of objects from a JSON file and convert them into dataclass instances.

    Args:
        filename (str): Path to the JSON file to load (relative to 'created/' mappa).
        cls (Type[T]): The dataclass type to instantiate (pl. Player, Race_Data).

    Returns:
        List[T]: A list of dataclass instances.
    """
    path = Path("created/jsons/") / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result: List[T] = []
    for item in data:
        if is_dataclass(cls):
            result.append(cls(**item))
        else:
            result.append(item)
    return result