"""Validate and filter jobs - Blue-Collar Bouncer."""

from src.job_scout.blocked_domains import is_domain_blocked
from src.job_scout.city_to_region import get_region
from src.job_scout.models import ValidatedJob, ValidatedJobsList
from src.job_scout.state import JobScoutState

VALIDATE_PROMPT = """Projdi všechny extrahované pracovní pozice a rozhodni, které PONECHAT a které ODSTRANIT.

PONECHAT (blue-collar / manuální práce):
- řidiči (kamion, dodávka, autobus, taxi)
- skladníci, manipulant
- výrobní dělníci, operátoři
- kurýři, rozvoz
- uklízeči, údržba
- prodejní personál (maloobchod)
- kuchaři, číšníci
- řemeslníci (elektrikář, instalatér, atd.)

ODSTRANIT:
- IT, vývojáři, programátoři
- HR, personalistika
- Marketing, PR
- Management, vedoucí pozice (kromě mistra, předáka)
- Pozice vyžadující VŠ vzdělání
- Administrativa, účetnictví

ZDROJ INZERÁTU:
- Pokud je zdrojem (source_url) firemní systém (Teamio, Recruitis, Greenhouse) a pozice splňuje blue-collar kritéria, PONECHEJ JI.
- Pokud je zdrojem obecný portál (Bazoš, Annonce) a inzerát nemá jasnou identifikaci firmy, ODSTRAŇ JEJ.

Deduplikuj podle kombinace Title + Company - každou unikátní pozici uveď jen jednou.

Vrať POUZE pozice, které PONECHAT."""


async def validate_filter_node(state: JobScoutState) -> dict:
    """Filter jobs for blue-collar roles and deduplicate."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    raw_jobs = [
        j for j in state.get("raw_extracted_jobs", [])
        if not is_domain_blocked(j.get("url", "")) and not is_domain_blocked(j.get("source_url", ""))
    ]
    loop_count = state.get("loop_count", 0)

    if not raw_jobs:
        print(f"[validate_filter] Žádné pozice k validaci (loop {loop_count + 1})")
        career_urls = state.get("career_candidate_urls", [])
        nav_links = state.get("discovered_nav_links", [])
        urls_to_exclude = list(career_urls) + list(nav_links)
        return {
            "formatted_results": [],
            "loop_count": loop_count + 1,
            "excluded_urls": urls_to_exclude,
            "all_formatted_results": [],
        }

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.1,
    )

    import json

    jobs_text = json.dumps(raw_jobs[:80], ensure_ascii=False, separators=(',', ':'))

    prompt = f"""{VALIDATE_PROMPT}

Pro každou pozici, kterou PONECHAT, vrať kompletní záznam včetně: position, company, city, region, contact, description, salary, url, source_url. Pole city, region a contact zkopíruj z extrahovaných dat; pokud tam nejsou, nech prázdné.

Extrahované pozice (JSON):
{jobs_text}
"""

    structured_llm = llm.with_structured_output(ValidatedJobsList)

    try:
        result = await structured_llm.ainvoke(
            [HumanMessage(content=prompt)],
            config={"run_name": "validate_filter_blue_collar"},
        )
        validated = result.jobs
    except Exception:
        validated = []

    user_input = state.get("user_input", {})
    fallback_city = user_input.get("city", "")

    seen = set()
    unique: list[dict] = []
    for v in validated:
        if is_domain_blocked(v.url) or is_domain_blocked(v.source_url):
            continue
        key = (v.position.lower().strip(), v.company.lower().strip())
        if key not in seen:
            seen.add(key)
            row = v.model_dump()
            # City z extrahovaných dat; pokud prázdné, fallback na město z uživatelského zadání
            if not (row.get("city") or "").strip():
                row["city"] = fallback_city
            # Region: fallback z mapy měst, pokud LLM neextrahoval
            if not (row.get("region") or "").strip() and (row.get("city") or "").strip():
                row["region"] = get_region(row["city"])
            unique.append(row)

    print(f"[validate_filter] raw_jobs: {len(raw_jobs)}, unique po validaci: {len(unique)}")

    career_urls = state.get("career_candidate_urls", [])
    nav_links = state.get("discovered_nav_links", [])
    urls_to_exclude = list(career_urls) + list(nav_links)

    return {
        "formatted_results": unique,
        "loop_count": loop_count + 1,
        "excluded_urls": urls_to_exclude,
        "all_formatted_results": unique,
    }
