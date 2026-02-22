#!/usr/bin/env python3
"""Workia Job Researcher - CLI entry point."""

import asyncio
from dotenv import load_dotenv

# Load environment variables first (before any imports that use them)
load_dotenv()


def _parse_int(prompt: str, default: int) -> int:
    """Načte číslo od uživatele, při neplatném vstupu vrátí default."""
    raw = input(prompt).strip() or str(default)
    try:
        return int(raw)
    except ValueError:
        return default


def get_user_input() -> dict:
    """Prompt user for input parameters."""
    print("=" * 50)
    print("Workia Job Researcher - Analýza odkazů")
    print("=" * 50)

    position = input("Pozice (např. řidič, skladník): ").strip() or "řidič"
    city = input("Město: ").strip() or "Praha"
    companies_per_run = _parse_int("Počet firem na běh (Exa výsledky) [10]: ", 10)
    max_career_links = _parse_int("Max. odkazů na kariéru na firmu (Serper) [5]: ", 5)
    max_nav_links_per_domain = _parse_int("Max. odkazů na crawl na doménu [5]: ", 5)
    num_repetitions = _parse_int("Počet opakování smyčky [1]: ", 1)

    return {
        "position": position,
        "city": city,
        "companies_per_run": companies_per_run,
        "max_career_links": max_career_links,
        "max_nav_links_per_domain": max_nav_links_per_domain,
        "num_repetitions": num_repetitions,
    }


async def main() -> None:
    """Run the job scout workflow."""
    from src.job_scout.graph import compile_graph
    from src.job_scout.state import JobScoutState

    user_input = get_user_input()
    print("\nSpouštím výzkum...\n")

    initial_state: JobScoutState = {
        "user_input": user_input,
        "loop_count": 0,
        "dynamic_exclude_domains": [],
        "excluded_urls": [],
        "all_formatted_results": [],
        "company_domains": [],
        "company_metadata": [],
        "career_candidate_urls": [],
        "discovered_nav_links": [],
        "raw_extracted_jobs": [],
        "formatted_results": [],
    }

    graph = compile_graph()
    result = await graph.ainvoke(initial_state)

    all_formatted = result.get("all_formatted_results", [])

    print("\n" + "=" * 60)
    print("VÝSLEDKY – Blue-collar pozice")
    print("=" * 60)

    # Souhrn
    user_input = result.get("user_input", {})
    position_req = user_input.get("position", "—")
    city_req = user_input.get("city", "—")
    unique_companies = len(
        {(j.get("company") or "").strip() for j in all_formatted if (j.get("company") or "").strip()}
    )
    num_positions = len(all_formatted)

    print(f"ZADÁNÍ:  pozice „{position_req}“, město {city_req}")
    print(f"FIRMY:   {unique_companies} unikátních")
    print(f"POZICE:  {num_positions} celkem")
    print("-" * 60)

    if all_formatted:
        for i, job in enumerate(all_formatted, 1):
            pos = job.get("position", "")
            company = job.get("company", "")
            salary = job.get("salary") or "neuvedeno"
            url = job.get("url", "")
            print(f"\n  {i}. {pos} @ {company}")
            print(f"     Plat: {salary}")
            print(f"     URL: {url}")
        print(f"\nCelkem: {len(all_formatted)} pozic")
        print("Export do vysledky.csv proběhl.")
    else:
        print("  Žádné blue-collar pozice nenalezeny.")


if __name__ == "__main__":
    asyncio.run(main())
