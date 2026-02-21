"""LLM filtr career_candidate_urls – ponechá jen URL, které mohou obsahovat volné pozice."""

from src.job_scout.llm_url_filter import filter_urls_with_llm
from src.job_scout.state import JobScoutState


async def filter_career_urls_llm_node(state: JobScoutState) -> dict:
    """Projde career_candidate_urls přes LLM a vrátí jen URL, které mohou obsahovat volné pozice."""
    career_urls = state.get("career_candidate_urls", [])
    if not career_urls:
        print("[filter_career_urls_llm] Žádné odkazy k filtrování")
        return {"career_candidate_urls": []}

    print("\n" + "=" * 60)
    print("[filter_career_urls_llm] PŘED filtrem –", len(career_urls), "URL")
    print("=" * 60)
    for i, url in enumerate(career_urls, 1):
        print(f"  {i}. {url}")
    print()

    filtered = await filter_urls_with_llm(career_urls, "filter_career_urls_llm")

    print("=" * 60)
    print("SEZNAM URL PO FILTRU (pro Crawl4AI) –", len(filtered), "URL")
    print("=" * 60)
    if filtered:
        for i, url in enumerate(filtered, 1):
            print(f"  {i}. {url}")
    else:
        print("  (žádné)")
    print()

    return {"career_candidate_urls": filtered}
