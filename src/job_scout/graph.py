"""LangGraph workflow definition for the job scout."""

from langgraph.graph import END, StateGraph

from src.job_scout.state import JobScoutState
from src.job_scout.nodes.query_gen import exa_query_gen_node
from src.job_scout.nodes.find_companies import find_companies_node
from src.job_scout.nodes.find_career_pages import find_career_pages_node


def compile_graph():
    """Build and compile the job scout workflow graph.

    Režim analýzy odkazů: končí po nalezení firem a kariérních stránek.
    Bez crawAI analýzy – vhodné pro postupné přidávání exclude domains.
    """
    graph = StateGraph(JobScoutState)

    graph.add_node("exa_query_gen", exa_query_gen_node)
    graph.add_node("find_companies", find_companies_node)
    graph.add_node("find_career_pages", find_career_pages_node)

    graph.set_entry_point("exa_query_gen")
    graph.add_edge("exa_query_gen", "find_companies")
    graph.add_edge("find_companies", "find_career_pages")
    graph.add_edge("find_career_pages", END)

    return graph.compile()
