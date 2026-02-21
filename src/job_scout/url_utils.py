"""URL normalization for consistent comparison."""

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize URL for comparison: lowercase, strip trailing slash, remove fragment."""
    if not url or not url.strip():
        return ""
    try:
        parsed = urlparse(url.strip())
        # Rebuild without fragment, with lowercase netloc
        normalized = urlunparse(
            (
                parsed.scheme.lower() if parsed.scheme else "",
                parsed.netloc.lower() if parsed.netloc else "",
                parsed.path.rstrip("/") or "/",
                parsed.params,
                parsed.query,
                "",  # no fragment
            )
        )
        return normalized
    except Exception:
        return url.strip().lower()


def is_url_excluded(url: str, excluded_set: set[str]) -> bool:
    """Check if URL is in excluded set (both normalized for comparison)."""
    return normalize_url(url) in excluded_set
