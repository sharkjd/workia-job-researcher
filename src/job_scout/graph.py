"""LangGraph workflow definition for the job scout."""

from langgraph.graph import END, StateGraph

from src.job_scout.state import JobScoutState
from src.job_scout.nodes.query_gen import exa_query_gen_node
from src.job_scout.nodes.find_companies import find_companies_node
from src.job_scout.nodes.find_career_pages import find_career_pages_node
from src.job_scout.nodes.analyze_initial import analyze_initial_pages_node
from src.job_scout.nodes.filter_nav_links_llm import filter_nav_links_llm_node
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
    graph.add_node("filter_nav_links_llm", filter_nav_links_llm_node)
    graph.add_node("crawl_deep", crawl_deep_links_node)
    graph.add_node("validate_filter", validate_filter_node)
    graph.add_node("export_csv", export_csv_node)

    graph.set_entry_point("exa_query_gen")
    graph.add_edge("exa_query_gen", "find_companies")
    graph.add_edge("find_companies", "find_career_pages")
    graph.add_edge("find_career_pages", "analyze_initial")
    graph.add_edge("analyze_initial", "filter_nav_links_llm")
    graph.add_edge("filter_nav_links_llm", "crawl_deep")
    graph.add_edge("crawl_deep", "validate_filter")

    def _should_continue(state: JobScoutState) -> str:
        """Pokud loop_count < num_repetitions, pokračuj další smyčkou, jinak export."""
        loop_count = state.get("loop_count", 0)
        num_repetitions = state.get("user_input", {}).get("num_repetitions", 1)
        if loop_count < num_repetitions:
            return "exa_query_gen"
        return "export_csv"

    graph.add_conditional_edges("validate_filter", _should_continue, ["exa_query_gen", "export_csv"])
    graph.add_edge("export_csv", END)

    return graph.compile()
