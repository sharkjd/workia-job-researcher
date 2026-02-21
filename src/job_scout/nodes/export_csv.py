"""Export formatted results to CSV file."""

import csv
from datetime import datetime

from src.job_scout.state import JobScoutState

CSV_PATH = "vysledky.csv"
FIELDNAMES = ["position", "company", "description", "salary", "url", "source_url"]


def _write_csv(path: str, rows: list[dict]) -> None:
    """Zapíše řádky do CSV souboru."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (v or "") for k, v in row.items() if k in FIELDNAMES})


async def export_csv_node(state: JobScoutState) -> dict:
    """Save all_formatted_results to CSV. Pro každý loop také separátní soubor s časovým razítkem."""
    all_results = state.get("all_formatted_results", [])
    loop_results = state.get("formatted_results", [])
    loop_count = state.get("loop_count", 1)

    # Celkový CSV (akumulovaný)
    _write_csv(CSV_PATH, all_results)
    print(f"[export_csv] Exportováno {len(all_results)} pozic do {CSV_PATH} (celkem)")

    # Separátní soubor pro tento loop
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    loop_path = f"vysledky_loop{loop_count}_{timestamp}.csv"
    _write_csv(loop_path, loop_results)
    print(f"[export_csv] Loop {loop_count}: {len(loop_results)} pozic do {loop_path}")

    return {}
