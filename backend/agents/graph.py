from langgraph.graph import StateGraph, END
from .state import ResearchState
from .nodes import (
    quran_research_node,
    weather_node,
    web_search_node,
    make_vector_store_node,
    formatter_node,
)


def create_research_graph(vector_store):
    """Build and compile the sequential LangGraph research pipeline."""
    vs_node = make_vector_store_node(vector_store)

    g = StateGraph(ResearchState)

    g.add_node("quran_researcher", quran_research_node)
    g.add_node("weather_reporter", weather_node)
    g.add_node("web_searcher", web_search_node)
    g.add_node("vector_storer", vs_node)
    g.add_node("formatter", formatter_node)

    g.set_entry_point("quran_researcher")
    g.add_edge("quran_researcher", "weather_reporter")
    g.add_edge("weather_reporter", "web_searcher")
    g.add_edge("web_searcher", "vector_storer")
    g.add_edge("vector_storer", "formatter")
    g.add_edge("formatter", END)

    return g.compile()
