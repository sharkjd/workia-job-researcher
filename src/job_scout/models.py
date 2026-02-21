"""Pydantic schemas for job extraction and validation."""

from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    """Single job offer extracted from a webpage."""

    position: str = Field(description="Job title or position name")
    description: str = Field(default="", description="Job description or summary")
    salary: str | None = Field(default=None, description="Salary information if available")
    url: str = Field(description="URL to the job posting")
    company: str = Field(default="", description="Company name")


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
