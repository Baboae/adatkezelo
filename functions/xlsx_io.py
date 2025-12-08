from openpyxl import Workbook, load_workbook
from pathlib import Path
from dataclasses import asdict, is_dataclass
from typing import List, Type, TypeVar
import json

T = TypeVar("T")

def save_xlsx(sheets: dict, filename: str) -> None:
    """
    Save multiple lists of dataclasses or dicts into separate sheets in an XLSX file.
    sheets: {"SheetName": [list_of_items], ...}
    """
    wb = Workbook()
    wb.remove(wb.active)

    for name, items in sheets.items():
        ws = wb.create_sheet(title=name)
        rows = [asdict(i) if is_dataclass(i) else i for i in items]
        if not rows:
            continue
        # flatten nested dict/list values into JSON strings
        def flatten(row):
            return {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
                    for k, v in row.items()}
        rows = [flatten(r) for r in rows]

        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row[h] for h in headers])

    path = Path("created/xlsxs") / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def load_xlsx(filename: str, sheet: str, cls: Type[T]) -> List[T]:
    """
    Load a sheet from XLSX and convert rows into dataclass instances.
    """
    path = Path("created/xlsxs") / filename
    wb = load_workbook(path)
    ws = wb[sheet]
    rows = list(ws.rows)
    headers = [cell.value for cell in rows[0]]
    result = []
    for row in rows[1:]:
        values = [cell.value for cell in row]
        data = dict(zip(headers, values))
        result.append(cls(**data))
    return result
