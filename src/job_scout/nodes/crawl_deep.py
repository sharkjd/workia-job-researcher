"""Crawl deep links (job listing pages) and extract full job details."""

import asyncio
from urllib.parse import urljoin, urlparse

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.job_scout.blocked_domains import is_domain_blocked
from src.job_scout.models import PageAnalysisResult
from src.job_scout.state import JobScoutState
from src.job_scout.url_utils import is_url_excluded, normalize_url

CRAWL_DEEP_PROMPT = """Extrahuj ze stránky se seznamem pracovních pozic všechny nabízené pozice.

Pro každou pozici uveď: position (název), description (krátký popis), salary (pokud je uveden), url (odkaz na detail), company (název firmy).

Obsah stránky (Markdown):
---
{markdown}
---
"""


async def crawl_deep_links_node(state: JobScoutState) -> dict:
    """Crawl discovered nav links and extract job details."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

    discovered = state.get("discovered_nav_links", [])
    excluded_urls = state.get("excluded_urls", [])
    excluded_set = {normalize_url(u) for u in excluded_urls if u}
    nav_links = [
        u for u in discovered
        if not is_domain_blocked(u) and not is_url_excluded(u, excluded_set)
    ]
    if not nav_links:
        print("[crawl_deep_links] Žádné odkazy na seznamy pozic – přeskakuji")
        return {}

    existing_jobs = state.get("raw_extracted_jobs", [])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(PageAnalysisResult)

    raw_jobs: list[dict] = []

    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in nav_links:
            try:
                result = await crawler.arun(url, config=run_config)
                await asyncio.sleep(1)

                if not result or not getattr(result, "success", True):
                    continue

                md = getattr(result, "markdown", None)
                if hasattr(md, "raw_markdown"):
                    markdown = md.raw_markdown or ""
                elif hasattr(md, "fit_markdown") and md.fit_markdown:
                    markdown = md.fit_markdown
                elif isinstance(md, str):
                    markdown = md
                else:
                    markdown = getattr(result, "markdown_v2", "") or ""
                if not markdown or len(markdown) < 50:
                    continue

                analysis = await structured_llm.ainvoke(
                    [HumanMessage(content=CRAWL_DEEP_PROMPT.format(markdown=markdown[:15000]))],
                    config={"run_name": "crawl_deep_links"},
                )

                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                for job in analysis.direct_offers:
                    job_dict = job.model_dump()
                    if job_dict.get("url") and not job_dict["url"].startswith("http"):
                        job_dict["url"] = urljoin(base_url, job_dict["url"])
                    job_dict["source_url"] = url
                    raw_jobs.append(job_dict)

            except Exception:
                continue

    print(f"[crawl_deep_links] Z hlubokých odkazů extrahováno {len(raw_jobs)} pozic")
    return {"raw_extracted_jobs": existing_jobs + raw_jobs}
