"""Find career pages for each company domain via Serper search."""

import asyncio
import os

import httpx

from src.job_scout.blocked_domains import is_domain_blocked
from src.job_scout.state import JobScoutState
from src.job_scout.url_utils import is_url_excluded, normalize_url

SERPER_URL = "https://google.serper.dev/search"


async def _serper_search(query: str, api_key: str) -> list[str]:
    """Search Serper and return list of URLs from organic results."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            SERPER_URL,
            json={"q": query},
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    urls: list[str] = []
    for item in data.get("organic", []):
        link = item.get("link")
        if link:
            urls.append(link)
    return urls


async def find_career_pages_node(state: JobScoutState) -> dict:
    """Find career page URLs for each company domain."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY is not set in environment")

    company_domains = state.get("company_domains", [])
    user_input = state.get("user_input", {})
    max_career_links = user_input.get("max_career_links", 5)
    excluded_urls = state.get("excluded_urls", [])
    excluded_set = {normalize_url(u) for u in excluded_urls if u}

    serper_raw_urls: list[str] = []

    for domain in company_domains:
        query = f'site:{domain} (kariéra OR práce OR volná místa OR jobs)'
        try:
            urls = await _serper_search(query, api_key)
            urls = urls[:max_career_links]
            if urls:
                filtered = [u for u in urls if not is_url_excluded(u, excluded_set)]
                serper_raw_urls.extend(filtered)
            else:
                fallback = f"https://{domain}"
                if not is_url_excluded(fallback, excluded_set):
                    serper_raw_urls.append(fallback)
            await asyncio.sleep(1)
        except Exception:
            fallback = f"https://{domain}"
            if not is_url_excluded(fallback, excluded_set):
                serper_raw_urls.append(fallback)

    career_candidate_urls = [u for u in serper_raw_urls if not is_domain_blocked(u)]

    print("\n" + "=" * 50)
    print("SEZNAM URL PO SERPER")
    print("=" * 50)
    for i, u in enumerate(serper_raw_urls, 1):
        print(f"  {i}. {u}")

    print("\n" + "=" * 50)
    print("SEZNAM URL ZE SERPERU (před LLM filtrem)")
    print("=" * 50)
    for i, u in enumerate(career_candidate_urls, 1):
        print(f"  {i}. {u}")

    return {
        "career_candidate_urls": career_candidate_urls,
        "serper_raw_urls": serper_raw_urls,
    }
