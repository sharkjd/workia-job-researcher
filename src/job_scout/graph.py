"""LangGraph workflow definition for the job scout."""

from typing import Literal

from langgraph.graph import END, StateGraph

from src.job_scout.state import JobScoutState
from src.job_scout.nodes.query_gen import exa_query_gen_node
from src.job_scout.nodes.find_companies import find_companies_node
from src.job_scout.nodes.find_career_pages import find_career_pages_node
from src.job_scout.nodes.analyze_initial import analyze_initial_pages_node
from src.job_scout.nodes.crawl_deep import crawl_deep_links_node
from src.job_scout.nodes.validate_filter import validate_filter_node
from src.job_scout.nodes.export_csv import export_csv_node


def route_after_validate(
    state: JobScoutState,
) -> Literal["find_companies", "export_csv"]:
    """Route to next loop or export based on loop count."""
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("user_input", {}).get("max_loops", 1)
    if loop_count < max_loops:
        return "find_companies"
    return "export_csv"


def compile_graph():
    """Build and compile the job scout workflow graph."""
    graph = StateGraph(JobScoutState)

    graph.add_node("exa_query_gen", exa_query_gen_node)
    graph.add_node("find_companies", find_companies_node)
    graph.add_node("find_career_pages", find_career_pages_node)
    graph.add_node("analyze_initial_pages", analyze_initial_pages_node)
    graph.add_node("crawl_deep_links", crawl_deep_links_node)
    graph.add_node("validate_filter", validate_filter_node)
    graph.add_node("export_csv", export_csv_node)

    graph.set_entry_point("exa_query_gen")
    graph.add_edge("exa_query_gen", "find_companies")
    graph.add_edge("find_companies", "find_career_pages")
    graph.add_edge("find_career_pages", "analyze_initial_pages")
    graph.add_edge("analyze_initial_pages", "crawl_deep_links")
    graph.add_edge("crawl_deep_links", "validate_filter")
    graph.add_conditional_edges(
        "validate_filter",
        route_after_validate,
        {"find_companies": "find_companies", "export_csv": "export_csv"},
    )
    graph.add_edge("export_csv", END)

    return graph.compile()
