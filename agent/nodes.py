# agent/nodes.py
from __future__ import annotations
from typing import Dict, List

from tools.search import web_search as real_search
from tools.scrape import scrape as real_scrape
from tools.llm import LLM


def web_search(state: Dict) -> Dict:
    q = state["query"]
    k = 8 if state.get("depth") == "deep" else 5
    results = real_search(q, k=k)              # <-- REAL API call
    state["search_results"] = {i: r for i, r in enumerate(results)}
    return state


def browse(state: Dict) -> Dict:
    results: List[Dict] = list(state.get("search_results", {}).values())[:8]
    docs: List[Dict] = []
    for r in results:
        url = (r.get("url") or "").strip()
        if not url:
            continue
        page = real_scrape(url)                # <-- REAL fetch + parse
        docs.append({
            "url": page["url"],
            "title": page.get("title") or r.get("title") or page["url"],
            "text": page["text"],
        })
    state["docs"] = docs
    return state


def write(state: Dict) -> Dict:
    llm = LLM()
    q = state["query"]
    docs: List[Dict] = state.get("docs", [])

    # Build real reference list
    refs, seen = [], set()
    for d in docs:
        url = (d.get("url") or "").strip()
        if not url or "example.com" in url or url in seen:
            continue
        seen.add(url)
        title = (d.get("title") or url).strip()
        refs.append(f"- [{title}]({url})")
    if not refs:
        refs.append("- No references collected (check API keys / network).")

    # Use scraped snippets as context
    context = "\n\n".join(d["text"][:1000] for d in docs[:5])
    system = "You are a careful research writer. Cite sources when appropriate."
    user = f"""Question: {q}

Use the following scraped snippets as context (they may be partial):

{context}

Write a clear, self-contained answer (200–400 words) and DO NOT fabricate citations."""
    body = llm.chat(system, user)

    state["draft"] = (
        f"# Draft\n\n**Question.** {q}\n\n{body}\n\n## References\n" + "\n".join(refs)
    )
    return state
