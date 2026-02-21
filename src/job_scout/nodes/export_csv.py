"""Export formatted results to CSV file."""

import csv
import os

from src.job_scout.state import JobScoutState

CSV_PATH = "vysledky.csv"
FIELDNAMES = ["position", "company", "description", "salary", "url", "source_url"]


async def export_csv_node(state: JobScoutState) -> dict:
    """Save formatted_results to CSV, append if file exists."""
    results = state.get("formatted_results", [])

    file_exists = os.path.isfile(CSV_PATH)
    write_header = not file_exists

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for row in results:
            writer.writerow({k: (v or "") for k, v in row.items() if k in FIELDNAMES})

    return {}
