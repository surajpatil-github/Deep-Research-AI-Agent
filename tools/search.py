# tools/search.py
from __future__ import annotations

import os
from typing import Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()


def _serpapi_key() -> str:
    # Support both names
    return os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY", "")


class SearchError(RuntimeError):
    pass


def _tavily(query: str, k: int) -> List[Dict[str, str]]:
    key = os.getenv("TAVILY_API_KEY", "")
    if not key:
        return []

    try:
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": key, "query": query, "max_results": k},
            timeout=25,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    out: List[Dict[str, str]] = []
    for r in (data.get("results") or []):
        out.append(
            {
                "title": (r.get("title") or r.get("url") or "result").strip(),
                "url": (r.get("url") or "").strip(),
                "snippet": (r.get("content") or "").strip()[:400],
            }
        )
    return out


def _serpapi(query: str, k: int) -> List[Dict[str, str]]:
    key = _serpapi_key()
    if not key:
        return []

    try:
        params = {"engine": "google", "q": query, "num": str(k), "api_key": key}
        r = requests.get("https://serpapi.com/search", params=params, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    organic = data.get("organic_results") or []
    out: List[Dict[str, str]] = []
    for r in organic[:k]:
        out.append(
            {
                "title": (r.get("title") or "result").strip(),
                "url": (r.get("link") or "").strip(),
                "snippet": (r.get("snippet") or "").strip()[:400],
            }
        )
    return out


def web_search(query: str, k: int = 6) -> List[Dict[str, str]]:
    """
    Public API used by nodes.web_search().
    Returns a list of {title, url, snippet}. Never raises; returns [] on failure.
    Prefers Tavily; falls back to SerpAPI.
    """
    k = max(1, min(int(k or 6), 20))  # simple bounds

    def _strip_examples(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [it for it in items if it.get("url") and "example.com" not in it["url"]]

    # Try Tavily (if key present)
    items = _strip_examples(_tavily(query, k))
    if items:
        return items

    # Fallback: SerpAPI (if key present)
    items = _strip_examples(_serpapi(query, k))
    if items:
        return items

    # No keys or both failed → return [] (nodes handle this gracefully)
    return []
