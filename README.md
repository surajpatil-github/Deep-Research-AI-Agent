# 🧠 Deep Research Agent

**An autonomous AI system for deep, verifiable knowledge discovery — powered by LangGraph, OpenAI, and Gradio.**

---

## 📘 Overview

**Deep Research Agent** is an **agentic AI workflow** that performs autonomous, multi-step research on any question or topic.  
It plans the research, searches the web, scrapes reliable sources, analyzes findings, critiques biases, and generates a well-structured summary with references.

This project integrates:
- **LangGraph** for agent orchestration (stateful DAG-based flow)
- **OpenAI GPT-4o-mini** for reasoning, analysis, and writing
- **SerpAPI** for intelligent web searching
- **Playwright** for dynamic page browsing (to bypass blocked/static sites)
- **Gradio** for a modern, interactive user interface

---

## 🚀 Features

✅ **End-to-End Research Automation**  
Plan → Search → Browse → Extract → Analyze → Critique → Write.

✅ **Deep Mode / Multi-Layer Thinking**  
Performs layered reasoning and critical analysis on results.

✅ **Source-Aware Scraping**  
Pulls only trusted, open-access sources (NIH, WHO, PubMed, etc.).  
Avoids 403/blocked domains like *pubs.acs.org* or *springer.com*.

✅ **Gradio UI**  
Simple, responsive interface for running autonomous research sessions.

✅ **Configurable Depth Levels**  
Choose *shallow*, *standard*, or *deep* exploration modes.

✅ **Agentic Workflow**  
Built as a modular **LangGraph DAG**, allowing flexible task chaining and parallelism.

---

## 🏗️ Architecture

ui/
└── gradio_app.py # Frontend interface

agent/
├── graph.py # LangGraph DAG definition
├── nodes.py # Research nodes (search, browse, analyze, critique)
└── state.py # State schema for the agent

tools/
├── search.py # SERPAPI / Tavily search integration
├── scrape.py # Playwright + BeautifulSoup extraction
└── llm.py # OpenAI LLM interface

.env # API keys and configuration



**Workflow Overview:**
1. `plan` – creates a structured query plan  
2. `search` – retrieves web results via SerpAPI  
3. `browse` – fetches and parses article content using Playwright  
4. `index` – extracts and filters key insights  
5. `analyze` – summarizes and compares findings  
6. `critic` – identifies contradictions or limitations  
7. `write` – generates a polished, referenced report

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<yourusername>/deep-research-agent.git
cd deep-research-agent


python -m venv .venv
.venv\Scripts\activate        # (Windows)
# or
source .venv/bin/activate     # (Linux/Mac)

pip install -r requirements.txt

pip uninstall -y cchardet
pip install chardet charset-normalizer

OPENAI_API_KEY="your_openai_api_key"
SERPAPI_API_KEY="your_serpapi_key"
TAVILY_API_KEY="your_tavily_key"        # optional
LANGCHAIN_API_KEY="your_langchain_key"
EMBEDDING_MODEL="text-embedding-3-small"
OPENAI_MODEL="gpt-4o-mini"
MAX_TOKENS="2000"
TEMPERATURE="0.2"

pip install playwright
python -m playwright install chromium

python -m ui.gradio_app
