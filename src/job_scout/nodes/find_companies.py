"""Discover company domains via Exa.ai semantic search."""

import asyncio
import os
from urllib.parse import urlparse

from src.job_scout.state import JobScoutState


def _extract_domain(url: str) -> str | None:
    """Extract root domain from URL."""
    try:
        parsed = urlparse(url)
        if parsed.netloc:
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
    except Exception:
        pass
    return None


async def find_companies_node(state: JobScoutState) -> dict:
    """Find company domains using Exa search, exclude already found domains."""
    from exa_py import Exa

    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY is not set in environment")

    query = state.get("exa_query", "")
    user_input = state.get("user_input", {})
    companies_per_run = user_input.get("companies_per_run", 10)
    dynamic_exclude = state.get("dynamic_exclude_domains", [])

    # Clear transient state for new loop iteration
    company_domains: list[str] = []
    new_exclude: list[str] = []

    exa = Exa(api_key=api_key)

    # Exa: excludeDomains not supported with category="company", use general search
    response = exa.search(
        query=query,
        num_results=companies_per_run,
        exclude_domains=dynamic_exclude if dynamic_exclude else None,
        type="auto",
        contents=False,
    )

    seen = set(dynamic_exclude)
    for result in response.results:
        url = getattr(result, "url", None) or getattr(result, "id", "")
        domain = _extract_domain(url)
        if domain and domain not in seen:
            seen.add(domain)
            company_domains.append(domain)
            new_exclude.append(domain)

    await asyncio.sleep(1)

    return {
        "company_domains": company_domains,
        "dynamic_exclude_domains": new_exclude,
        "career_candidate_urls": [],
        "discovered_nav_links": [],
    }
