"""
DeepEval + pytest test suite for the Research Agent.

Run with:
    cd backend
    pytest tests/ -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Unit tests — tools (no LLM needed)
# ---------------------------------------------------------------------------

class TestQuranTool:
    def test_returns_results(self):
        from agents.tools import search_quran
        results = search_quran("patience", limit=3)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_result_has_reference(self):
        from agents.tools import search_quran
        results = search_quran("patience", limit=2)
        for r in results:
            assert "reference" in r

    def test_graceful_on_bad_query(self):
        from agents.tools import search_quran
        results = search_quran("xyzxyzxyzxyz123", limit=2)
        assert isinstance(results, list)  # must not raise


class TestPrayerTimesTool:
    def test_london(self):
        from agents.tools import get_prayer_times
        times = get_prayer_times("London", "UK")
        assert isinstance(times, dict)

    def test_main_prayers_present(self):
        from agents.tools import get_prayer_times
        times = get_prayer_times("London", "UK")
        if "error" not in times:
            for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                assert prayer in times


class TestWebSearchTool:
    def test_returns_list(self):
        from agents.tools import web_search
        results = web_search("climate change 2024", max_results=2)
        assert isinstance(results, list)
        assert len(results) > 0


class TestGuardrails:
    def test_valid_topic(self):
        from guardrails import validate_input
        ok, _ = validate_input("gratitude in Islam")
        assert ok

    def test_too_short(self):
        from guardrails import validate_input
        ok, msg = validate_input("hi")
        assert not ok
        assert "short" in msg.lower()

    def test_blocked_topic(self):
        from guardrails import validate_input
        ok, _ = validate_input("violence methods")
        assert not ok

    def test_html_injection(self):
        from guardrails import validate_input
        ok, _ = validate_input("<script>alert(1)</script>")
        assert not ok

    def test_valid_output(self):
        from guardrails import validate_output
        ok, _ = validate_output("A" * 100)
        assert ok

    def test_empty_output(self):
        from guardrails import validate_output
        ok, _ = validate_output("")
        assert not ok


class TestVectorStore:
    def test_store_and_search(self):
        from vector_store import VectorStoreManager
        vs = VectorStoreManager()
        vs.store_documents(["Patience is a virtue in Islam", "Sabr means patience"], "patience")
        results = vs.search("patience virtue", n_results=2)
        assert isinstance(results, list)

    def test_empty_search(self):
        from vector_store import VectorStoreManager
        vs = VectorStoreManager()
        results = vs.search("something")
        assert results == []


# ---------------------------------------------------------------------------
# DeepEval quality tests (requires OPENAI_API_KEY)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — skipping DeepEval tests",
)
class TestDeepEvalQuality:
    def test_answer_relevancy(self):
        from deepeval.test_case import LLMTestCase
        from deepeval.metrics import AnswerRelevancyMetric

        test_case = LLMTestCase(
            input="What does Islam say about gratitude?",
            actual_output=(
                "In Islam, gratitude (shukr) is a central virtue. The Quran states in 14:7: "
                "'If you are grateful, I will surely increase you in favor.' "
                "Gratitude to Allah is considered both a spiritual practice and a moral obligation."
            ),
        )
        metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
        metric.measure(test_case)
        assert metric.score >= 0.7, f"Relevancy too low: {metric.score}"

    def test_faithfulness(self):
        from deepeval.test_case import LLMTestCase
        from deepeval.metrics import FaithfulnessMetric

        test_case = LLMTestCase(
            input="What does the Quran say about knowledge?",
            actual_output=(
                "The Quran emphasises seeking knowledge. Surah Al-Alaq (96:1) is the "
                "first revelation: 'Read in the name of your Lord.'"
            ),
            retrieval_context=[
                "Surah Al-Alaq (96:1): Read in the name of your Lord who created.",
                "Quran 20:114: My Lord, increase me in knowledge.",
            ],
        )
        metric = FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini")
        metric.measure(test_case)
        assert metric.score >= 0.7, f"Faithfulness too low: {metric.score}"

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        from agents.graph import create_research_graph
        from agents.state import ResearchState
        from vector_store import VectorStoreManager

        vs = VectorStoreManager()
        graph = create_research_graph(vs)
        state: ResearchState = {
            "topic": "gratitude",
            "city": "London",
            "country": "UK",
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
        final = await graph.ainvoke(state)
        assert final["final_report"], "Report should not be empty"
        assert len(final["agent_steps"]) == 5, "All 5 agents should have run"
