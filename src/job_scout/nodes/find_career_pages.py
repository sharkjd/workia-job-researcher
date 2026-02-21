"""Find career pages for each company domain via Serper search."""

import asyncio
import os

import httpx
from src.job_scout.state import JobScoutState

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

    career_candidate_urls: list[str] = []

    for domain in company_domains:
        query = f'site:{domain} (kariéra OR práce OR "volná místa" OR jobs)'
        try:
            urls = await _serper_search(query, api_key)
            urls = urls[:max_career_links]
            if urls:
                career_candidate_urls.extend(urls)
            else:
                career_candidate_urls.append(f"https://{domain}")
            await asyncio.sleep(1)
        except Exception:
            career_candidate_urls.append(f"https://{domain}")

    return {"career_candidate_urls": career_candidate_urls}
