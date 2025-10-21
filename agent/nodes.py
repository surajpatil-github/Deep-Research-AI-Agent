from __future__ import annotations

from typing import Any, Dict, List

from dotenv import load_dotenv, find_dotenv
from tools.search import web_search as real_search
from tools.scrape import scrape as real_scrape
from tools.llm import LLM  # ✅ keep a single, consistent import path

# Load environment from project .env (do not override existing env)
load_dotenv(find_dotenv(), override=False)






def web_search(state: dict) -> dict:
    q = state.get("query") or state.get("question") or state.get("prompt")
    if not q:
        raise KeyError("No query/question/prompt found in state.")

    # Call search tool safely
    try:
        results = real_search(q) or []
    except Exception as e:
        print(f"[web_search] search backend error: {e}")
        results = []

    if not isinstance(results, list):
        print("[web_search] non-list result from search tool; coercing to []")
        results = []

    # Normalize + dedupe by domain (robust)
    normalized, seen_domains = {}, set()
    i = 1

    def _domain(u: str) -> str:
        try:
            if "://" in u:
                return u.split("/", 3)[2]
            return u.split("/", 1)[0]
        except Exception:
            return u

    for item in results:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or "").strip()
        if not url:
            continue
        title = (item.get("title") or url).strip()
        snippet = (item.get("snippet") or "").strip()

        dom = _domain(url)
        if dom in seen_domains:
            continue
        seen_domains.add(dom)

        normalized[f"r{i}"] = {"url": url, "title": title, "snippet": snippet}
        i += 1
        if i > 12:
            break

    # If domain-dedupe killed everything, fall back to first few raw results
    if not normalized:
        print("[web_search] domain dedupe produced 0; falling back to first results")
        j = 1
        for item in results[:6]:
            if not isinstance(item, dict):
                continue
            url = (item.get("url") or "").strip()
            if not url:
                continue
            normalized[f"r{j}"] = {
                "url": url,
                "title": (item.get("title") or url).strip(),
                "snippet": (item.get("snippet") or "").strip(),
            }
            j += 1

    state["search_results"] = normalized
    print(f"[web_search] stored {len(normalized)} results")
    return state


import math

MIN_CHARS = 300           # ↓ was 800; too strict for abstracts/landing pages
MAX_DOCS = 10
MAX_TEXT_PER_DOC = 10000

def _safe_scrape(url: str) -> Dict[str, str]:
    try:
        # remove timeout kwarg if your scraper doesn't support it
        page = real_scrape(url, timeout=20)  # type: ignore
        if not isinstance(page, dict):
            print(f"[browse] scrape non-dict for {url}")
            return {}
        text = (page.get("text") or "").strip()
        if not text:
            print(f"[browse] empty text for {url}")
            return {}
        if len(text) < MIN_CHARS:
            print(f"[browse] thin page ({len(text)} chars) for {url}")
            # still return it; we'll use it rather than discard
        return {
            "url": (page.get("url") or url).strip(),
            "title": (page.get("title") or url).strip(),
            "text": text[:MAX_TEXT_PER_DOC],
        }
    except Exception as e:
        print(f"[browse] scrape error for {url}: {e}")
        return {}

def browse(state: Dict) -> Dict:
    results: List[Dict] = list(state.get("search_results", {}).values())[:MAX_DOCS]
    print(f"[browse] incoming results: {len(results)}")
    docs: List[Dict] = []

    for r in results:
        url = (r.get("url") or "").strip()
        title = (r.get("title") or url).strip()
        snippet = (r.get("snippet") or "").strip()
        if not url:
            continue

        page = _safe_scrape(url)

        if page:
            # Use scraped page; if it's thin but has some text, still keep it
            page["snippet"] = snippet
            docs.append(page)
        else:
            # 🔁 Fallback: if scrape failed, build a doc from the search snippet
            if snippet:
                print(f"[browse] using snippet fallback for {url}")
                docs.append({
                    "url": url,
                    "title": title,
                    "text": snippet[:MAX_TEXT_PER_DOC],
                    "snippet": snippet,
                })
            else:
                print(f"[browse] skipped {url}: no scrape and no snippet")

    print(f"[browse] docs collected: {len(docs)}")
    state["docs"] = docs
    return state


def _chunks(s: str, size: int = 1200, max_chunks: int = 6):
    out, i = [], 0
    while i < len(s) and len(out) < max_chunks:
        out.append(s[i:i+size])
        i += size
    return out

def write(state: Dict) -> Dict:
    llm = LLM(temperature=0.2, max_tokens=700)  # be crisp, reduce rambling
    q = state["query"]
    docs: List[Dict] = state.get("docs", [])

    if not docs:
        state["draft"] = (
            f"# Draft\n\n**Question.** {q}\n\n"
            "I couldn’t fetch any usable sources. Please check API keys/network or try a different query.\n"
        )
        return state

    # Build references + map ids
    refs, seen = [], {}
    for idx, d in enumerate(docs, start=1):
        url = (d.get("url") or "").strip()
        title = (d.get("title") or url).strip()
        if not url or url in seen:
            continue
        seen[url] = idx
        refs.append(f"[{idx}] {title} — {url}")

    # Compose contextual snippets from top docs (chunked)
    context_blocks = []
    for d in docs[:5]:
        title = d.get("title") or d.get("url")
        cid = seen.get(d.get("url"))
        for ch in _chunks(d.get("text",""))[:2]:
            context_blocks.append(f"(Source {cid}: {title})\n{ch}")

    context = "\n\n---\n\n".join(context_blocks[:8])

    system = (
        "You are a careful research writer. Use only the provided context."
        " When asserting facts, add inline citations like [1], [2]."
        " Never invent sources or numbers not present in context."
    )
    user = f"""Question: {q}

Use ONLY these snippets (may be partial). If you aren't sure, say so briefly.

{context}

Write a clear, self-contained answer (~250–400 words) with inline citations [n].
End with a short 2–3 bullet 'Key sources' section listing the cited source numbers."""
    body = llm.chat(system, user)

    refs_md = "\n".join(f"- {r}" for r in refs) if refs else "- (no references)"
    state["draft"] = (
        f"# Draft\n\n**Question.** {q}\n\n{body}\n\n## References\n{refs_md}\n"
    )
    return state
