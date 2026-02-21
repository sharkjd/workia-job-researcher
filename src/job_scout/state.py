"""LangGraph state definition for the job scout workflow."""

import operator
from typing import Annotated, TypedDict


class JobScoutState(TypedDict, total=False):
    """State for the Workia Job Researcher workflow."""

    user_input: dict
    exa_query: str
    loop_count: int
    dynamic_exclude_domains: Annotated[list[str], operator.add]
    excluded_urls: Annotated[list[str], operator.add]
    all_formatted_results: Annotated[list[dict], operator.add]
    company_domains: list[str]  # Replaced each loop by find_companies
    career_candidate_urls: list[str]  # Replaced each loop by find_career_pages
    discovered_nav_links: list[str]  # Replaced each loop by find_companies/analyze_initial
    raw_extracted_jobs: list[dict]  # Replaced each loop; merged by analyze_initial + crawl_deep
    formatted_results: list[dict]  # Replaced by validate_filter
