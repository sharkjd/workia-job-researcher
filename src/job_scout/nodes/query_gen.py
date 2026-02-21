"""Generate semantic search query for Exa.ai."""

from src.job_scout.state import JobScoutState


QUERY_GEN_PROMPT = """Vygeneruj sémantický vyhledávací dotaz pro Exa.ai, který najde webové stránky firem v městě {city}, které zaměstnávají pozici {position}.

Zaměř se na obchodní entity jako: logistické areály, výrobní závody, dopravní společnosti, sklady, distribuce.
NEVYHLEDÁVEJ job boardy ani portály s inzeráty.

Vrať POUZE samotný vyhledávací dotaz, žádný další text."""


async def exa_query_gen_node(state: JobScoutState) -> dict:
    """Generate Exa semantic search query from user input."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    user_input = state["user_input"]
    position = user_input.get("position", "řidič")
    city = user_input.get("city", "Praha")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )

    prompt = QUERY_GEN_PROMPT.format(position=position, city=city)
    response = await llm.ainvoke(
        [HumanMessage(content=prompt)],
        config={"run_name": "exa_query_gen"},
    )

    query = response.content.strip().strip('"').strip("'")
    print(f"[exa_query_gen] Vygenerován dotaz: {query[:60]}{'...' if len(query) > 60 else ''}")
    return {"exa_query": query}
