import json
from typing import List, Any
from dataclasses import asdict, is_dataclass
from data.basic.model_classes import *

def save_to_json(items: List[Any], filename: str) -> None:
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

    with open(f"created/{filename}", "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=4, ensure_ascii=False)