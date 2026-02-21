"""Discover company domains via Exa.ai semantic search."""

import asyncio
import os
from urllib.parse import urlparse

from src.job_scout.blocked_domains import is_domain_blocked
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
    # contents s textem pro snippety pro company_triage
    response = exa.search(
        query=query,
        num_results=companies_per_run,
        exclude_domains=dynamic_exclude if dynamic_exclude else None,
        type="auto",
        contents={"text": {"maxCharacters": 400}},
    )

    company_metadata: list[dict] = []
    seen = set(dynamic_exclude)
    for result in response.results:
        url = getattr(result, "url", None) or getattr(result, "id", "")
        domain = _extract_domain(url)
        if domain and domain not in seen and not is_domain_blocked(domain):
            seen.add(domain)
            company_domains.append(domain)
            new_exclude.append(domain)

            # Snippet z textu nebo highlights
            snippet = ""
            text = getattr(result, "text", None)
            if text:
                snippet = (text[:400] + "...") if len(text) > 400 else text
            else:
                highlights = getattr(result, "highlights", None) or []
                if highlights:
                    snippet = " ".join(str(h) for h in highlights[:3])[:400]
            title = getattr(result, "title", None) or ""

            company_metadata.append({
                "domain": domain,
                "snippet": snippet,
                "title": title,
            })

    await asyncio.sleep(1)

    print("\n" + "=" * 50)
    print("SEZNAM DOMÉN Z EXA.AI")
    print("=" * 50)
    for i, d in enumerate(company_domains, 1):
        print(f"  {i}. {d}")

    return {
        "company_domains": company_domains,
        "company_metadata": company_metadata,
        "exa_raw_domains": company_domains,
        "dynamic_exclude_domains": new_exclude,
        "career_candidate_urls": [],
        "discovered_nav_links": [],
        "raw_extracted_jobs": [],
        "formatted_results": [],
    }
