# tests/test_pipeline.py
from __future__ import annotations

from unittest.mock import patch
from agent.graph import app


def _fake_search(query: str, k: int = 6):
    return [
        {"title": "Paper 1", "url": "https://example.org/p1", "snippet": "quantum annealing overview"},
        {"title": "Paper 2", "url": "https://example.org/p2", "snippet": "gate-model vs annealing"},
    ]


def _fake_scrape(url: str):
    return {
        "url": url,
        "title": "Mock Page",
        "text": (
            "Quantum annealing optimizes Ising models via energy minimization, "
            "while gate-model quantum computing uses universal gates and circuits. "
            "They differ in control, universality, and error models."
        ),
    }


class _DummyLLM:
    def __init__(self, *_, **__): ...
    def chat(self, system: str, user: str) -> str:
        return "Here is a concise draft comparing quantum annealing and gate-model QC."


def test_basic():
    state = {
        "query": "What is quantum annealing and how does it differ from gate-model quantum computing?",
        "depth": "standard",
        "subtasks": [],
        "search_results": {},
        "docs": [],
        "chunks": [],
        "citations": [],
        "notes": [],
        "draft": None,
        "quality": {"score": 0, "iterations": 0},
    }

    with patch("agent.nodes.web_search", side_effect=_fake_search), \
         patch("agent.nodes.scrape", side_effect=_fake_scrape), \
         patch("tools.search.web_search", side_effect=_fake_search), \
         patch("tools.scrape.scrape", side_effect=_fake_scrape), \
         patch("tools.llm.LLM", _DummyLLM):

        out = app.invoke(state)

    assert out.get("draft"), "Pipeline produced no draft"
