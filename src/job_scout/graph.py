"""LangGraph workflow definition for the job scout."""

from langgraph.graph import END, StateGraph

from src.job_scout.state import JobScoutState
from src.job_scout.nodes.query_gen import exa_query_gen_node
from src.job_scout.nodes.find_companies import find_companies_node
from src.job_scout.nodes.company_triage import company_triage_node
from src.job_scout.nodes.find_career_pages import find_career_pages_node
from src.job_scout.nodes.analyze_initial import analyze_initial_pages_node
from src.job_scout.nodes.filter_career_urls_llm import filter_career_urls_llm_node
from src.job_scout.nodes.filter_nav_links_llm import filter_nav_links_llm_node
from src.job_scout.nodes.crawl_deep import crawl_deep_links_node
from src.job_scout.nodes.validate_filter import validate_filter_node
from src.job_scout.nodes.export_csv import export_csv_node


def compile_graph():
    """Build and compile the job scout workflow graph.

    Pipeline: Exa → Triage → Serper → Filter career URLs (LLM) → Analyze → Filter nav URLs (LLM) → Crawl Deep → Validate → Export.
    Po export_csv: pokud loop_count < num_repetitions, pokračuje na find_companies (nová iterace s vyloučenými doménami), jinak END.
    """
    graph = StateGraph(JobScoutState)

    graph.add_node("exa_query_gen", exa_query_gen_node)
    graph.add_node("find_companies", find_companies_node)
    graph.add_node("company_triage", company_triage_node)
    graph.add_node("find_career_pages", find_career_pages_node)
    graph.add_node("filter_career_urls_llm", filter_career_urls_llm_node)
    graph.add_node("analyze_initial", analyze_initial_pages_node)
    graph.add_node("filter_nav_links_llm", filter_nav_links_llm_node)
    graph.add_node("crawl_deep", crawl_deep_links_node)
    graph.add_node("validate_filter", validate_filter_node)
    graph.add_node("export_csv", export_csv_node)

    graph.set_entry_point("exa_query_gen")
    graph.add_edge("exa_query_gen", "find_companies")
    graph.add_edge("find_companies", "company_triage")
    graph.add_edge("company_triage", "find_career_pages")
    graph.add_edge("find_career_pages", "filter_career_urls_llm")
    graph.add_edge("filter_career_urls_llm", "analyze_initial")
    graph.add_edge("analyze_initial", "filter_nav_links_llm")
    graph.add_edge("filter_nav_links_llm", "crawl_deep")
    graph.add_edge("crawl_deep", "validate_filter")
    graph.add_edge("validate_filter", "export_csv")

    def _should_continue(state: JobScoutState) -> str:
        """Vrátí 'continue' pro další iteraci, nebo 'end' pro konec."""
        user_input = state.get("user_input", {})
        num_repetitions = user_input.get("num_repetitions", 1)
        loop_count = state.get("loop_count", 0)
        if loop_count < num_repetitions:
            return "continue"
        return "end"

    graph.add_conditional_edges(
        "export_csv",
        _should_continue,
        {"continue": "find_companies", "end": END},
    )

    return graph.compile()
