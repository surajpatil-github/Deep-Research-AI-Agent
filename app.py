# app.py
  
from __future__ import annotations

from tools.env_bootstrap import *  

import sys
from dotenv import load_dotenv

from agent.graph import app

load_dotenv()

def main():
    q = " ".join(sys.argv[1:]).strip() or "Impacts of microplastics on human health"
    state = {
        "query": q,
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
    out = app.invoke(state)
    print(out.get("draft", "❌ No draft produced."))

if __name__ == "__main__":
    main()
