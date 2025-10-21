# ui/gradio_app.py
 

from __future__ import annotations

from tools.brotli_patch import *   

from tools.env_bootstrap import *  
import gradio as gr
from dotenv import load_dotenv

from agent.graph import app
from agent.state import AgentState

from agent.graph import build_app
app = build_app()


load_dotenv()

STYLES = """
#log {white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}
"""

def run(query: str, depth: str) -> str:
    query = (query or "").strip()
    if not query:
        return "⚠️ Please enter a research question."

    state: AgentState = {
        "query": query,
        "depth": depth,
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
    return out.get("draft", "❌ No draft produced.")

with gr.Blocks(css=STYLES, title="Deep Research Agent") as demo:
    gr.Markdown("## 🔎 Deep Research Agent")

    q = gr.Textbox(
        label="Research Question",
        lines=3,
        placeholder="e.g., What is the evidence that ultra-processed foods increase all-cause mortality?",
    )
    depth = gr.Radio(choices=["shallow", "standard", "deep"], value="deep", label="Depth")
    run_btn = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    run_btn.click(fn=run, inputs=[q, depth], outputs=report)
    
if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", server_port=7860)
