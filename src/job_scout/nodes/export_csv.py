"""Export formatted results to CSV file."""

import csv

from src.job_scout.state import JobScoutState

CSV_PATH = "vysledky.csv"
FIELDNAMES = ["position", "company", "description", "salary", "url", "source_url"]


async def export_csv_node(state: JobScoutState) -> dict:
    """Save all_formatted_results to CSV (results from all loop repetitions)."""
    results = state.get("all_formatted_results", [])

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in results:
            writer.writerow({k: (v or "") for k, v in row.items() if k in FIELDNAMES})

    print(f"[export_csv] Exportováno {len(results)} pozic do {CSV_PATH}")
    return {}
