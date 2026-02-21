"""Triage companies: filter out aggregators/portals, keep real companies."""

import asyncio
import re
from typing import Any

import httpx

from src.job_scout.blocked_domains import is_domain_blocked
from src.job_scout.models import TriageResult
from src.job_scout.state import JobScoutState

TRIAGE_PROMPT = """Jsi expert na klasifikaci webů. Tvým úkolem je odlišit weby KONKRÉTNÍCH FIRM od AGREGÁTORŮ, PORTÁLŮ a KATALOGŮ.

FIRMA: Web prezentuje vlastní služby, historii, vozový park, výrobu nebo provoz konkrétní firmy (např. autodoprava, pekárna, továrna, sklad).
AGREGÁTOR/PORTÁL: Web nabízí seznamy inzerátů od mnoha firem, databáze kontaktů, vyhledávání práce (např. Jobs.cz, Bazoš.cz, Firmy.cz, LinkedIn, Indeed).

Pro každou doménu s popiskem rozhodni: je to FIRMA nebo AGREGÁTOR?
Vrať POUZE seznam ověřených firemních domén (verified_domains) – tedy ty, které jsou skutečné firmy."""

# Klíčová slova v title/description pro vyřazení
PORTAL_KEYWORDS = ("inzeráty", "práce z celé čr", "katalog firem", "nabídky práce")


async def _fetch_page_meta(domain: str) -> tuple[str, str]:
    """Stáhne title a meta description z domény. Timeout 2s."""
    title, desc = "", ""
    url = f"https://{domain}" if "://" not in domain else domain
    try:
        async with httpx.AsyncClient(timeout=2.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return title, desc

    # <title>
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I | re.S)
    if m:
        title = m.group(1).strip()[:500]

    # <meta name="description" content="...">
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        html,
        re.I,
    )
    if m:
        desc = m.group(1).strip()[:500]

    return title, desc


def _is_portal_by_meta(title: str, description: str) -> bool:
    """True pokud title nebo description obsahuje známky portálu."""
    combined = f"{title} {description}".lower()
    return any(kw in combined for kw in PORTAL_KEYWORDS)


async def _http_fallback_filter(metadata: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pro každou doménu stáhne title+meta, vyřadí portály."""
    filtered: list[dict[str, Any]] = []
    for item in metadata:
        domain = item.get("domain", "")
        if not domain:
            continue
        title, desc = await _fetch_page_meta(domain)
        if _is_portal_by_meta(title, desc):
            continue
        filtered.append(item)
        await asyncio.sleep(0.2)  # Mírné omezení rychlosti
    return filtered


async def company_triage_node(state: JobScoutState) -> dict:
    """Filter out aggregators/portals, keep only real company domains."""
    company_domains = state.get("company_domains", [])
    company_metadata = state.get("company_metadata", [])

    if not company_domains:
        return {"company_domains": [], "company_metadata": []}

    # Sloučit metadata do mapy domain -> {snippet, title}
    meta_by_domain: dict[str, dict] = {}
    for m in company_metadata:
        d = m.get("domain", "")
        if d:
            meta_by_domain[d] = {
                "domain": d,
                "snippet": m.get("snippet", ""),
                "title": m.get("title", ""),
            }

    # HTTP fallback: vyřadit zjevné portály podle title/meta
    candidates = [
        meta_by_domain.get(d, {"domain": d, "snippet": "", "title": ""})
        for d in company_domains
        if not is_domain_blocked(d)
    ]
    after_http = await _http_fallback_filter(candidates)
    if not after_http:
        return {"company_domains": [], "company_metadata": []}

    # LLM analýza
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.1,
    )

    input_text = "\n".join(
        f"- {m['domain']}: title={m.get('title','')} | snippet={m.get('snippet','')[:200]}"
        for m in after_http
    )

    prompt = f"""{TRIAGE_PROMPT}

Seznam domén a jejich popisků:
{input_text}

Vrať JSON s polem verified_domains obsahujícím pouze domény skutečných firem."""

    structured_llm = llm.with_structured_output(TriageResult)

    try:
        result = await structured_llm.ainvoke(
            [HumanMessage(content=prompt)],
            config={"run_name": "company_triage"},
        )
        verified = result.verified_domains
    except Exception:
        verified = [m["domain"] for m in after_http]

    verified_set = {d.lower().strip() for d in verified if d}
    final_domains = [d for d in company_domains if d.lower() in verified_set]
    final_metadata = [m for m in company_metadata if m.get("domain", "").lower() in verified_set]

    print("\n" + "=" * 50)
    print("SEZNAM DOMÉN PO FILTRU LLM (company_triage)")
    print("=" * 50)
    for i, d in enumerate(final_domains, 1):
        print(f"  {i}. {d}")

    return {
        "company_domains": final_domains,
        "company_metadata": final_metadata,
    }
