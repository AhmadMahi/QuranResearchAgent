import asyncio
import os
from langchain_openai import ChatOpenAI
from .state import ResearchState
from .tools import search_quran, get_prayer_times, get_weather, web_search

_llm = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    return _llm


# ── Agent Nodes ──────────────────────────────────────────────────────────────

async def quran_research_node(state: ResearchState) -> dict:
    """Fetches relevant Quran verses for the topic."""
    topic = state["topic"]
    refs = await asyncio.to_thread(search_quran, topic, 5)
    valid = [r for r in refs if r.get("text")]
    return {
        "quran_references": refs,
        "agent_steps": [f"✓ Quran Research Agent — found {len(valid)} verse(s)"],
        "current_agent": "weather_reporter",
    }


async def weather_node(state: ResearchState) -> dict:
    """Fetches current weather and prayer times for the given city."""
    city = state.get("city") or "Mecca"
    country = state.get("country") or "Saudi Arabia"
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "")

    weather, prayer = await asyncio.gather(
        asyncio.to_thread(get_weather, city, api_key),
        asyncio.to_thread(get_prayer_times, city, country),
    )

    label = f"✓ Weather & Prayer Agent — {city}"
    return {
        "weather_data": weather,
        "prayer_times": prayer,
        "agent_steps": [label],
        "current_agent": "web_searcher",
    }


async def web_search_node(state: ResearchState) -> dict:
    """Runs an IslamQA-focused DuckDuckGo search for the topic."""
    query = state["topic"]
    results = await asyncio.to_thread(web_search, query, 5)
    found = len([r for r in results if r.get("url")])
    return {
        "web_results": results,
        "agent_steps": [f"✓ Web Search Agent — {found} IslamQA reference(s)"],
        "current_agent": "vector_storer",
    }


def make_vector_store_node(vs):
    """Factory — binds a VectorStoreManager instance to the node."""

    async def vector_store_node(state: ResearchState) -> dict:
        docs = []
        for r in state.get("quran_references", []):
            if r.get("text"):
                docs.append(r["text"])
        for r in state.get("web_results", [])[:4]:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            url = r.get("url", "")
            docs.append(f"{title}\n{snippet}\nSource: {url}"[:600])

        if docs:
            await asyncio.to_thread(vs.store_documents, docs, state["topic"])
            context = await asyncio.to_thread(vs.search, state["topic"], 3)
        else:
            context = []

        return {
            "vector_context": context,
            "agent_steps": [f"✓ Knowledge Base Agent — stored {len(docs)} doc(s)"],
            "current_agent": "formatter",
        }

    return vector_store_node


async def formatter_node(state: ResearchState) -> dict:
    """Synthesises all research into a structured markdown report."""
    topic = state["topic"]
    city = state.get("city", "")
    refs = state.get("quran_references", [])
    prayer = state.get("prayer_times", {})
    weather = state.get("weather_data", {})
    web = state.get("web_results", [])
    ctx = state.get("vector_context", [])

    sections = []

    if refs and any(r.get("text") for r in refs):
        lines = "\n".join(
            f"- **{r['reference']}**: {r['text'][:300]}" for r in refs[:3] if r.get("text")
        )
        sections.append(f"### Quranic References\n{lines}")

    if prayer and "error" not in prayer:
        prayer_lines = "\n".join(f"| {k} | {v} |" for k, v in prayer.items())
        sections.append(
            f"### Prayer Times — {city}\n| Prayer | Time |\n|--------|------|\n{prayer_lines}"
        )

    if weather and "error" not in weather and "note" not in weather:
        sections.append(
            f"### Current Weather — {weather.get('city', city)}\n"
            f"**{weather.get('description', '').title()}** · "
            f"{weather.get('temperature', 'N/A')} °C (feels like {weather.get('feels_like', 'N/A')} °C) · "
            f"Humidity {weather.get('humidity', 'N/A')}% · "
            f"Wind {weather.get('wind_speed', 'N/A')} m/s"
        )

    if web:
        lines = []
        for r in web[:5]:
            title = r.get("title", "Untitled")
            snippet = (r.get("snippet") or "")[:220]
            url = r.get("url") or ""
            if url:
                lines.append(f"- [{title}]({url}) — {snippet}")
            else:
                lines.append(f"- {title} — {snippet}")
        sections.append("### IslamQA References (DuckDuckGo)\n" + "\n".join(lines))

    if ctx:
        sections.append(f"### Semantic Context\n" + "\n".join(f"- {c[:200]}" for c in ctx[:2]))

    research_data = "\n\n".join(sections)

    prompt = f"""You are an expert research analyst. Write a comprehensive, well-structured research report on:

**Topic:** {topic}

**Gathered Research Data:**
{research_data if research_data else "General knowledge only — no external data retrieved."}

---
Structure the report with these markdown sections:
1. ## Executive Summary
2. ## Quranic & Spiritual Perspective (if relevant data exists)
3. ## Current Context (weather / local context if available)
4. ## Research Findings
5. ## Key Insights & Recommendations
6. ## Conclusion
7. ## References

In the References section, include explicit source links from IslamQA data when available.
Be professional, insightful, and concrete. Use bullet points where appropriate."""

    resp = await asyncio.to_thread(get_llm().invoke, prompt)

    return {
        "final_report": resp.content,
        "agent_steps": ["✓ Report Formatter Agent — report generated"],
        "current_agent": "complete",
    }
