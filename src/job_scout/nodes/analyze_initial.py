"""Analyze career pages with Crawl4AI and extract jobs via Gemini."""

import asyncio
from urllib.parse import urljoin, urlparse

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.job_scout.blocked_domains import is_domain_blocked
from src.job_scout.models import PageAnalysisResult
from src.job_scout.state import JobScoutState

ANALYZE_PROMPT = """Analyzuj tuto webovou stránku a extrahuj:

1. **direct_offers**: Seznam pracovních pozic přímo na této stránce (název, popis, plat pokud je, URL, firma).
2. **navigation_links**: Absolutní URL odkazů na tlačítka typu "Aktuální volná místa", "See all positions", "Kariéra", "Všechny pozice" - odkazy které vedou na seznam všech nabízených pozic.

Pokud je to homepage, hledej v menu nebo patičce odkaz na Kariéru.
Pokud je to seznam pozic, extrahuj jednotlivé nabídky.

Obsah stránky (Markdown):
---
{markdown}
---
"""


async def analyze_initial_pages_node(state: JobScoutState) -> dict:
    """Crawl career candidate URLs and extract jobs + nav links via LLM."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

    urls = [u for u in state.get("career_candidate_urls", []) if not is_domain_blocked(u)]
    if not urls:
        print("[analyze_initial_pages] Žádné kariérní stránky k analýze")
        return {"raw_extracted_jobs": [], "discovered_nav_links": []}

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
    )
    structured_llm = llm.with_structured_output(PageAnalysisResult)

    raw_jobs: list[dict] = []
    nav_links: list[str] = []

    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
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
                    [HumanMessage(content=ANALYZE_PROMPT.format(markdown=markdown[:15000]))],
                    config={"run_name": "analyze_initial_pages"},
                )

                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                for job in analysis.direct_offers:
                    job_dict = job.model_dump()
                    if job_dict.get("url") and not job_dict["url"].startswith("http"):
                        job_dict["url"] = urljoin(base_url, job_dict["url"])
                    job_dict["source_url"] = url
                    raw_jobs.append(job_dict)

                for link in analysis.navigation_links:
                    full_url = urljoin(base_url, link) if link and not link.startswith("http") else link
                    if full_url and not is_domain_blocked(full_url):
                        nav_links.append(full_url)

            except Exception:
                continue

    print(f"[analyze_initial_pages] Extrahováno {len(raw_jobs)} pozic, {len(nav_links)} odkazů na seznamy")
    return {
        "raw_extracted_jobs": raw_jobs,
        "discovered_nav_links": nav_links,
    }
