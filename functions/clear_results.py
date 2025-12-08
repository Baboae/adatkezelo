from pathlib import Path

def clear_results():
    base = Path("created")
    for fmt in ["jsons/race_results", "csvs/race_results", "xlsxs/race_results"]:
        results_dir = base / fmt
        results_dir.mkdir(parents=True, exist_ok=True)
        for file in results_dir.iterdir():
            if file.is_file():
                file.unlink()
