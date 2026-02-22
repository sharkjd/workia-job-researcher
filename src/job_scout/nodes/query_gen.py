"""Generate semantic search query for Exa.ai."""

from src.job_scout.state import JobScoutState


QUERY_GEN_PROMPT = """Vygeneruj sémantický vyhledávací dotaz pro Exa.ai, který najde webové stránky firem v městě {city}, které zaměstnávají pozici {position}.

Hledáme výhradně weby konkrétních firem (např. firma.cz, dopravni-spolecnost.cz), ne portály pro hledání práce jako jobs.cz, Prace.cz, Indeed, LinkedIn Jobs apod.

Zaměř se na obchodní entity jako: logistické areály, výrobní závody, dopravní společnosti, sklady, distribuce.
NEVYHLEDÁVEJ job boardy ani agregátory inzerátů.

Vrať POUZE samotný vyhledávací dotaz, žádný další text."""


EXA_FIXED_QUERY = "Najdi webové stránky firem v Praze a středních Čechách, které jsou výrobní závody, logistické areály, dopravní společnosti, sklady nebo distribuční centra a zaměstnávají CNC operátory. Vyluč pracovní portály a agregátory nabídek práce."


async def exa_query_gen_node(state: JobScoutState) -> dict:
    """Generate Exa semantic search query from user input."""
    # from langchain_google_genai import ChatGoogleGenerativeAI
    # from langchain_core.messages import HumanMessage

    # user_input = state["user_input"]
    # position = user_input.get("position", "řidič")
    # city = user_input.get("city", "Praha")

    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     temperature=0.3,
    # )

    # prompt = QUERY_GEN_PROMPT.format(position=position, city=city)
    # response = await llm.ainvoke(
    #     [HumanMessage(content=prompt)],
    #     config={"run_name": "exa_query_gen"},
    # )

    # query = response.content.strip().strip('"').strip("'")
    query = EXA_FIXED_QUERY

    print("\n" + "=" * 50)
    print("PROMPT PRO EXA.AI")
    print("=" * 50)
    print(query)

    return {"exa_query": query}
