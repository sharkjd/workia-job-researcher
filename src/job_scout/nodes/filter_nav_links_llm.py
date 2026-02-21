"""LLM filtr odkazů – ponechá jen URL, které mohou obsahovat volné pozice."""

from src.job_scout.llm_url_filter import filter_urls_with_llm
from src.job_scout.state import JobScoutState


async def filter_nav_links_llm_node(state: JobScoutState) -> dict:
    """Projde discovered_nav_links přes LLM a vrátí jen URL, které mohou obsahovat volné pozice."""
    discovered = state.get("discovered_nav_links", [])
    if not discovered:
        print("[filter_nav_links_llm] Žádné odkazy k filtrování")
        return {"discovered_nav_links": []}

    print("\n" + "=" * 60)
    print("[filter_nav_links_llm] PŘED filtrem –", len(discovered), "URL")
    print("=" * 60)
    for i, url in enumerate(discovered, 1):
        print(f"  {i}. {url}")
    print()

    filtered = await filter_urls_with_llm(discovered, "filter_nav_links_llm")

    print("=" * 60)
    print("[filter_nav_links_llm] PO filtru –", len(filtered), "URL")
    print("=" * 60)
    if filtered:
        for i, url in enumerate(filtered, 1):
            print(f"  {i}. {url}")
    else:
        print("  (žádné)")
    print()

    return {"discovered_nav_links": filtered}
