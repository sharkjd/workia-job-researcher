"""LangGraph state definition for the job scout workflow."""

import operator
from typing import Annotated, TypedDict


class JobScoutState(TypedDict, total=False):
    """State for the Workia Job Researcher workflow."""

    user_input: dict
    exa_query: str
    loop_count: int
    dynamic_exclude_domains: Annotated[list[str], operator.add]
    company_domains: list[str]  # Replaced each loop by find_companies
    career_candidate_urls: list[str]  # Replaced each loop by find_career_pages
    discovered_nav_links: list[str]  # Replaced each loop by find_companies/analyze_initial
    raw_extracted_jobs: Annotated[list[dict], operator.add]
    formatted_results: list[dict]  # Replaced by validate_filter
