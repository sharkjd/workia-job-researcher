"""LLM filtr odkazů – ponechá jen URL, které mohou obsahovat volné pozice."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.job_scout.models import FilteredUrlsResult
from src.job_scout.state import JobScoutState
from src.job_scout.url_utils import normalize_url

FILTER_PROMPT = """Máš seznam URL z firemních webů. Označ (vyber) pouze ty, které pravděpodobně mohou obsahovat seznam pracovních pozic, volných míst nebo kariéru.

Vyřaď URL, které evidentně vedou na:
- GDPR, ochrana osobních údajů, cookies, obchodní podmínky
- Služby firmy (pronájem, provozování, dílna, servis)
- Produkty, e-shop, katalog
- Novinky, blog, aktuality
- Kontakt, o nás, reference, certifikace

Vrať pouze URL, u kterých existuje reálná šance, že na stránce najdu seznam volných pracovních míst.

Důležité: Hlavní domény bez podstránky (např. https://firma.cz/ nebo https://www.firma.cz/) vždy ponech – některé weby mají kariéru přímo na homepage.

Seznam URL:
---
{urls}
---
"""

BATCH_SIZE = 60


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

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(FilteredUrlsResult)

    filtered: list[str] = []
    seen: set[str] = set()
    discovered_normalized = {normalize_url(u): u for u in discovered}
    for i in range(0, len(discovered), BATCH_SIZE):
        batch = discovered[i : i + BATCH_SIZE]
        urls_text = "\n".join(batch)
        result = await structured_llm.ainvoke(
            [HumanMessage(content=FILTER_PROMPT.format(urls=urls_text))],
            config={"run_name": "filter_nav_links_llm"},
        )
        for u in result.urls:
            norm = normalize_url(u)
            if norm in discovered_normalized and norm not in seen:
                seen.add(norm)
                filtered.append(discovered_normalized[norm])

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
