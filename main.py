#!/usr/bin/env python3
"""Workia Job Researcher - CLI entry point."""

import asyncio
from dotenv import load_dotenv

# Load environment variables first (before any imports that use them)
load_dotenv()


def get_user_input() -> dict:
    """Prompt user for input parameters."""
    print("=" * 50)
    print("Workia Job Researcher - Blue-Collar Edition")
    print("=" * 50)

    position = input("Pozice (např. řidič, skladník): ").strip() or "řidič"
    city = input("Město: ").strip() or "Praha"
    companies_per_run = int(
        input("Počet firem na běh (Exa výsledky) [10]: ").strip() or "10"
    )
    max_loops = int(input("Max. počet smyček [2]: ").strip() or "2")
    max_career_links = int(
        input("Max. odkazů na kariéru na firmu [5]: ").strip() or "5"
    )

    return {
        "position": position,
        "city": city,
        "companies_per_run": companies_per_run,
        "max_loops": max_loops,
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

    print("\n" + "=" * 50)
    print(f"Nalezeno {len(result.get('formatted_results', []))} relevantních pozic.")
    print("Výsledky uloženy do vysledky.csv")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
