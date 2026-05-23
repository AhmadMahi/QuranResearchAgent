from typing import TypedDict, List, Dict, Any, Annotated
import operator


class ResearchState(TypedDict):
    # User input
    topic: str
    city: str
    country: str

    # Agent outputs
    quran_references: List[Dict[str, Any]]
    prayer_times: Dict[str, str]
    weather_data: Dict[str, Any]
    web_results: List[Dict[str, str]]
    vector_context: List[str]
    final_report: str

    # Metadata — uses reducer so nodes append rather than overwrite
    agent_steps: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    current_agent: str
