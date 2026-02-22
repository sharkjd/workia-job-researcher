"""Pydantic schemas for job extraction and validation."""

from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    """Single job offer extracted from a webpage."""

    position: str = Field(description="Job title or position name")
    description: str = Field(default="", description="Job description or summary")
    salary: str | None = Field(default=None, description="Salary information if available")
    url: str = Field(description="URL to the job posting")
    company: str = Field(default="", description="Company name")
    city: str = Field(default="", description="City or location where the job is (e.g. Praha, Brno, Nepomuk)")
    region: str = Field(default="", description="Region (kraj) according to company - e.g. Praha, Středočeský kraj, Liberecký kraj")
    contact: str = Field(default="", description="Phone number and/or contact person name (who to call)")


class PageAnalysisResult(BaseModel):
    """Result of LLM analysis of a career page."""

    direct_offers: list[ExtractedJob] = Field(
        default_factory=list,
        description="Jobs found directly on this page",
    )
    navigation_links: list[str] = Field(
        default_factory=list,
        description="Absolute URLs to 'view all jobs' or similar pages",
    )


class ValidatedJob(BaseModel):
    """Final validated job for CSV export."""

    position: str
    company: str
    city: str = ""
    region: str = ""
    contact: str = ""
    description: str
    salary: str | None = None
    url: str
    source_url: str = Field(description="URL of the page where job was found")


class FilteredUrlsResult(BaseModel):
    """Výsledek LLM filtrování URL – pouze ty, které mohou obsahovat volné pozice."""

    urls: list[str] = Field(
        default_factory=list,
        description="URL, které pravděpodobně vedou na stránky se seznamem pracovních pozic",
    )


class ValidatedJobsList(BaseModel):
    """Wrapper for list of validated jobs (for LLM structured output)."""

    jobs: list[ValidatedJob] = Field(default_factory=list)


class TriageResult(BaseModel):
    """Výsledek LLM triage – ověřené firemní domény."""

    verified_domains: list[str] = Field(
        default_factory=list,
        description="Seznam domén, které jsou skutečné firmy (ne agregátory)",
    )
