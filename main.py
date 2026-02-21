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
    max_career_links = _parse_int("Max. odkazů na kariéru na firmu [5]: ", 5)

    return {
        "position": position,
        "city": city,
        "companies_per_run": companies_per_run,
        "max_career_links": max_career_links,
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
        "company_domains": [],
        "career_candidate_urls": [],
        "discovered_nav_links": [],
        "raw_extracted_jobs": [],
        "formatted_results": [],
    }

    graph = compile_graph()
    result = await graph.ainvoke(initial_state)

    company_domains = result.get("company_domains", [])
    career_urls = result.get("career_candidate_urls", [])

    print("\n" + "=" * 50)
    print("NALEZENÉ FIRMY (domény z Exa)")
    print("=" * 50)
    for i, domain in enumerate(company_domains, 1):
        print(f"  {i}. {domain}")

    print("\n" + "=" * 50)
    print("KARIÉRNÍ ODKAZY (URL z Serper)")
    print("=" * 50)
    for i, url in enumerate(career_urls, 1):
        print(f"  {i}. {url}")

    print("\n" + "=" * 50)
    print(f"Celkem: {len(company_domains)} firem, {len(career_urls)} odkazů")
    print("Pro exclude domains uprav src/job_scout/blocked_domains.py")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
