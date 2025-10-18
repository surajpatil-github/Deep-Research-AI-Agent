from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent import nodes

def build_app():
    g = StateGraph(AgentState)
    g.set_entry_point("search")
    g.add_node("search", nodes.web_search)
    g.add_node("browse", nodes.browse)
    g.add_node("write", nodes.write)
    g.add_edge("search", "browse")
    g.add_edge("browse", "write")
    g.add_edge("write", END)
    return g.compile()

app = build_app()
