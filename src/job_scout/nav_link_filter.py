"""Filtrování a limitování odkazů na kariéru před crawl_deep."""

from collections import defaultdict
from urllib.parse import urlparse

# Cesty, které téměř jistě nejsou kariérové stránky
NON_CAREER_PATH_PATTERNS = (
    "/p/",  # produktové stránky (traso.cz/p/...)
    "/produkt",
    "/product",
    "/produkty",
    "/products",
    "/katalog",
    "/catalog",
    "/eshop",
    "/e-shop",
    "/kosik",
    "/cart",
    "/basket",
    "/checkout",
    "/news/",
    "/aktuality",
    "/blog",
    "/clanky",
    "/prihlasit",
    "/login",
    "/registrace",
    "/account",
    "/vyroba-",
    "/servis",
    "/sluzby",
    "/reference",
    "/certifikace",
    "/projekty-eu",
    "/bazar",
    "/a/",  # články (traso.cz/a/prevozni-nadrze)
    "/hadice",
    "/cerpadla",
    "/prutokomery",
    "/vydejni-",
    "/skladovani-a-vydej-",
    # Právní, GDPR, cookies
    "/gdpr",
    "/privacy",
    "/ochrana-udaju",
    "/cookies",
    "/obchodni-podminky",
    "/terms",
    "/impressum",
    # Služby, provoz, pronájem (odos-cargo.cz atd.)
    "/pronajem",
    "/provozovani",
    "/dilna",
    "/pojizdna-",
    "/nabidka-",
)

# Rozšíření souborů – tyto URL přeskočit
NON_CAREER_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".pdf",
    ".zip",
    ".css",
    ".js",
)


def is_likely_non_career(url: str) -> bool:
    """Vrátí True, pokud URL na první pohled není kariérová stránka."""
    if not url or len(url) < 10:
        return True
    try:
        parsed = urlparse(url)
        path = parsed.path or ""
        path_lower = path.lower().rstrip("/") or "/"
        # Rozšíření souborů
        if any(path_lower.endswith(ext) for ext in NON_CAREER_EXTENSIONS):
            return True
        # Blacklist cest
        if any(seg in path_lower for seg in NON_CAREER_PATH_PATTERNS):
            return True
        # Query nebo fragment s product/manufacturer filtry (např. manufacturer-11=1)
        query_frag = ((parsed.query or "") + (parsed.fragment or "")).lower()
        if "manufacturer-" in query_frag:
            return True
        return False
    except Exception:
        return True


def filter_career_candidates(urls: list[str]) -> list[str]:
    """Vyřadí URL, které evidentně nevedou na kariéru."""
    return [u for u in urls if u and not is_likely_non_career(u)]


def limit_per_domain(urls: list[str], max_per_domain: int) -> list[str]:
    """Pro každou doménu ponechá max max_per_domain odkazů (první v pořadí)."""
    by_domain: dict[str, list[str]] = defaultdict(list)
    for u in urls:
        try:
            domain = urlparse(u).netloc.lower()
            if domain and len(by_domain[domain]) < max_per_domain:
                by_domain[domain].append(u)
        except Exception:
            continue
    result = []
    for domain_links in by_domain.values():
        result.extend(domain_links)
    return result
