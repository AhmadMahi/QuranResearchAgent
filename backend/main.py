import json
import os

from dotenv import load_dotenv

load_dotenv()

# LangSmith tracing — set before importing langchain modules
os.environ.setdefault("LANGCHAIN_TRACING_V2", os.getenv("LANGSMITH_TRACING", "false"))
os.environ.setdefault("LANGCHAIN_PROJECT", "SimpleResearchAgent")
os.environ.setdefault("LANGCHAIN_CALLBACKS_BACKGROUND", "false")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents.graph import create_research_graph
from agents.state import ResearchState
from guardrails import validate_input, validate_output, sanitize
from vector_store import VectorStoreManager

app = FastAPI(title="Research Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton — one in-memory store per server process
_vector_store = VectorStoreManager()
_graph = create_research_graph(_vector_store)


class ResearchRequest(BaseModel):
    topic: str
    city: str = "Mecca"
    country: str = "Saudi Arabia"


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/research")
async def research(req: ResearchRequest):
    topic = sanitize(req.topic)
    city = sanitize(req.city)
    country = sanitize(req.country)

    ok, msg = validate_input(topic, city, country)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    initial_state: ResearchState = {
        "topic": topic,
        "city": city,
        "country": country,
        "quran_references": [],
        "prayer_times": {},
        "weather_data": {},
        "web_results": [],
        "vector_context": [],
        "final_report": "",
        "agent_steps": [],
        "errors": [],
        "current_agent": "quran_researcher",
    }

    async def generate():
        yield {
            "event": "status",
            "data": json.dumps({"step": "🔬 Research pipeline starting…", "agent": "supervisor"}),
        }

        final_state = None
        prev_step_count = 0

        try:
            async for state in _graph.astream(initial_state, stream_mode="values"):
                steps = state.get("agent_steps", [])
                for step in steps[prev_step_count:]:
                    yield {
                        "event": "step",
                        "data": json.dumps({
                            "step": step,
                            "agent": state.get("current_agent", ""),
                        }),
                    }
                prev_step_count = len(steps)
                final_state = state

            if final_state is None:
                yield {"event": "error", "data": json.dumps({"message": "No output from pipeline"})}
                return

            report = final_state.get("final_report", "")
            ok_out, msg_out = validate_output(report)
            if not ok_out:
                yield {"event": "error", "data": json.dumps({"message": msg_out})}
                return

            yield {
                "event": "complete",
                "data": json.dumps({
                    "report": report,
                    "quran_references": final_state.get("quran_references", []),
                    "prayer_times": final_state.get("prayer_times", {}),
                    "weather_data": final_state.get("weather_data", {}),
                    "web_results": final_state.get("web_results", []),
                    "steps": final_state.get("agent_steps", []),
                }),
            }

        except Exception as exc:
            yield {"event": "error", "data": json.dumps({"message": str(exc)})}

    return EventSourceResponse(generate())
