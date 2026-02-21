"""LangGraph workflow definition for the job scout."""

from langgraph.graph import END, StateGraph

from src.job_scout.state import JobScoutState
from src.job_scout.nodes.query_gen import exa_query_gen_node
from src.job_scout.nodes.find_companies import find_companies_node
from src.job_scout.nodes.find_career_pages import find_career_pages_node
from src.job_scout.nodes.analyze_initial import analyze_initial_pages_node
from src.job_scout.nodes.crawl_deep import crawl_deep_links_node
from src.job_scout.nodes.validate_filter import validate_filter_node
from src.job_scout.nodes.export_csv import export_csv_node


def compile_graph():
    """Build and compile the job scout workflow graph.

    Plný pipeline: Exa → Serper → Crawl4AI analýza → validace blue-collar → export CSV.
    """
    graph = StateGraph(JobScoutState)

    graph.add_node("exa_query_gen", exa_query_gen_node)
    graph.add_node("find_companies", find_companies_node)
    graph.add_node("find_career_pages", find_career_pages_node)
    graph.add_node("analyze_initial", analyze_initial_pages_node)
    graph.add_node("crawl_deep", crawl_deep_links_node)
    graph.add_node("validate_filter", validate_filter_node)
    graph.add_node("export_csv", export_csv_node)

    graph.set_entry_point("exa_query_gen")
    graph.add_edge("exa_query_gen", "find_companies")
    graph.add_edge("find_companies", "find_career_pages")
    graph.add_edge("find_career_pages", "analyze_initial")
    graph.add_edge("analyze_initial", "crawl_deep")
    graph.add_edge("crawl_deep", "validate_filter")
    graph.add_edge("validate_filter", "export_csv")
    graph.add_edge("export_csv", END)

    return graph.compile()
