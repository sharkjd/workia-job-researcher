"""Validate and filter jobs - Blue-Collar Bouncer."""

from src.job_scout.blocked_domains import is_domain_blocked
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
        return {
            "formatted_results": [],
            "loop_count": loop_count + 1,
        }

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.1,
    )

    import json

    jobs_text = json.dumps(raw_jobs[:80], ensure_ascii=False, separators=(',', ':'))

    prompt = f"""{VALIDATE_PROMPT}

Pro každou pozici, kterou PONECHAT, vrať kompletní záznam včetně: position, company, description, salary, url, source_url.

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

    seen = set()
    unique: list[dict] = []
    for v in validated:
        if is_domain_blocked(v.url) or is_domain_blocked(v.source_url):
            continue
        key = (v.position.lower().strip(), v.company.lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(v.model_dump())

    return {
        "formatted_results": unique,
        "loop_count": loop_count + 1,
    }
