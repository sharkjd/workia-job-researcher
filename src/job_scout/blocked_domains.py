"""Blocked domains - exact match only. jobs.cz blocks jobs.cz, NOT teta.jobs.cz."""

from urllib.parse import urlparse

# Normalizované domény (lowercase, bez www) - exact match
BLOCKED_DOMAINS: frozenset[str] = frozenset({
    # Job portály
    "jobs.cz",
    "profesia.cz",
    "prace.cz",
    "práce.cz",
    "xn--prce-0va.cz",  # práce.cz (IDNA/punycode)
    "jobdnes.cz",
    "dobraprace.cz",
    "pracezarohem.cz",
    "grafton.cz",
    "novinator.cz",
    "easy-prace.cz",
    "jenprace.cz",
    "jenfirmy.cz",
    "pracomat.cz",
    "upcr.cz",
    "inzerce-dnes.cz",
    "ostravadnes.cz",
    "linkedin.com",
    "instagram.com",
    "careerjet.cz",
    "cz.jooble.org",
    "indeed.com",
    "glassdoor.com",
    "jobeka",
    "firmy.cz",
    "ifirmy.cz",
    "volnamista.cz",
    "profesia.sk",
    # Zpravodajství / ekonomika
    "logistika.ekonom.cz",
    "logistika.ihned.cz",
    "dnoviny.cz",
    "systemylogistiky.cz",
    "praktickalogistika.cz",
    "economia.cz",
    "ceskatelevize.cz",
    "ct24.ceskatelevize.cz",
    "aktualne.cz",
    "zpravy.aktualne.cz",
    # Vzdělávací instituce
    "jobs.pef.czu.cz",
    "cs.wikipedia.org",
    "wikipedia.org",
    "is.slu.cz",
    "slu.cz",
    "is.muni.cz",
    # Ostatní
    "rejstrik-firem.kurzy.cz",
    "amsp.cz",
    "floowie.com",
    "svn.apache.org",
})


def extract_domain(url_or_domain: str) -> str | None:
    """Extrahuje a normalizuje doménu z URL nebo čisté domény."""
    if not url_or_domain or not isinstance(url_or_domain, str):
        return None
    s = url_or_domain.strip().lower()
    if not s:
        return None
    # Pokud vypadá jako URL (má scheme), parsuj
    if "://" in s or s.startswith("//"):
        try:
            parsed = urlparse(s if "://" in s else f"https://{s}")
            if parsed.netloc:
                domain = parsed.netloc
            else:
                return None
        except Exception:
            return None
    else:
        # Čistá doména
        domain = s.split("/")[0].split(":")[0]
    domain = domain.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain if domain else None


def is_domain_blocked(url_or_domain: str) -> bool:
    """Vrací True, pokud je doména v BLOCKED_DOMAINS (exact match)."""
    domain = extract_domain(url_or_domain)
    return domain is not None and domain in BLOCKED_DOMAINS
