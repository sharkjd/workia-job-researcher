"""Sdílená logika LLM filtrování URL – ponechá jen ty, které mohou obsahovat volné pozice."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.job_scout.models import FilteredUrlsResult
from src.job_scout.url_utils import normalize_url

FILTER_PROMPT = """Máš seznam URL z firemních webů. Vyber POUZE ty URL, které mají reálnou šanci obsahovat pracovní nabídky nebo seznam volných míst.

PONECH jen URL, kde z cesty nebo domény lze usoudit, že jde o kariéru/práci – typicky obsahují slova jako: kariera, kariéra, prace, práce, volne-mista, volné pozice, jobs, career, nabidky-prace, pozice, karierni-stranka a podobné.

VYŘAĎ vše ostatní, zejména:
- blog, články, novinky, aktuality
- produkty, služby, katalog, e-shop
- GDPR, cookies, obchodní podmínky
- URL, u kterých z cesty nelze poznat, že jde o kariéru (např. jen /sluzby/, /o-nas/, /produkty/)

Vrať pouze URL, u kterých je z cesty jasné nebo pravděpodobné, že vedou na stránku s pracovními nabídkami.

Seznam URL:
---
{urls}
---
"""

BATCH_SIZE = 60


async def filter_urls_with_llm(urls: list[str], run_name: str) -> list[str]:
    """Pošle URL do LLM a vrátí jen ty, které mohou obsahovat volné pozice."""
    if not urls:
        return []

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(FilteredUrlsResult)

    filtered: list[str] = []
    seen: set[str] = set()
    urls_normalized = {normalize_url(u): u for u in urls}
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        urls_text = "\n".join(batch)
        result = await structured_llm.ainvoke(
            [HumanMessage(content=FILTER_PROMPT.format(urls=urls_text))],
            config={"run_name": run_name},
        )
        for u in result.urls:
            norm = normalize_url(u)
            if norm in urls_normalized and norm not in seen:
                seen.add(norm)
                filtered.append(urls_normalized[norm])
    return filtered
