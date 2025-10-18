# tools/search.py
from __future__ import annotations

import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class SearchError(RuntimeError):
    pass


def _tavily(query: str, k: int) -> List[Dict[str, str]]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise SearchError("TAVILY_API_KEY missing")

    resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": api_key, "query": query, "max_results": k},
        timeout=25,
    )
    if resp.status_code != 200:
        raise SearchError(f"Tavily error {resp.status_code}: {resp.text}")

    data = resp.json()
    out = []
    for r in data.get("results", []):
        out.append(
            {
                "title": r.get("title") or r.get("url") or "result",
                "url": r.get("url", ""),
                "snippet": (r.get("content") or "")[:400],
            }
        )
    return out


def _serpapi(query: str, k: int) -> List[Dict[str, str]]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise SearchError("SERPAPI_API_KEY missing")

    params = {
        "engine": "google",
        "q": query,
        "num": str(k),
        "api_key": api_key,
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=25)
    if resp.status_code != 200:
        raise SearchError(f"SerpAPI error {resp.status_code}: {resp.text}")

    organic = resp.json().get("organic_results", []) or []
    out: List[Dict[str, str]] = []
    for r in organic[:k]:
        out.append(
            {
                "title": r.get("title", "result"),
                "url": r.get("link", ""),
                "snippet": (r.get("snippet") or "")[:400],
            }
        )
    return out


def web_search(query: str, k: int = 6) -> List[Dict[str, str]]:
    """
    Return a list of {title, url, snippet}. No example.com placeholders.
    Prefers Tavily; falls back to SerpAPI.
    """
    def strip_examples(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [it for it in items if it.get("url") and "example.com" not in it["url"]]

    if os.getenv("TAVILY_API_KEY"):
        items = strip_examples(_tavily(query, k))
        if items:
            return items

    if os.getenv("SERPAPI_API_KEY"):
        items = strip_examples(_serpapi(query, k))
        if items:
            return items

    raise SearchError("Set TAVILY_API_KEY or SERPAPI_API_KEY to enable web search.")
