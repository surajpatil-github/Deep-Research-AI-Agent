# agent/state.py
from __future__ import annotations
from typing import Dict, List, Optional, TypedDict, Any

class AgentState(TypedDict, total=False):
    query: str                      # "shallow" | "standard" | "deep" can live in depth
    depth: str
    subtasks: List[str]
    search_results: Dict[str, Dict[str, str]]   # <-- CHANGED int -> str
    docs: List[Dict[str, str]]                  # OK (url, title, text, snippet)
    chunks: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
    notes: List[str]
    draft: Optional[str]
    quality: Dict[str, int]          # {"score": int, "iterations": int}
