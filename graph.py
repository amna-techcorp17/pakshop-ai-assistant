from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.router_agent import RouterAgent
from agents.rag_agent import RAGAgent
from agents.general_agent import GeneralAgent
from agents.evaluator_agent import EvaluatorAgent

class AgentState(TypedDict):
    query: str
    route: Optional[str]
    response: Optional[str]
    context: Optional[str]
    evaluation: Optional[dict]

router = RouterAgent()
rag = RAGAgent()
general = GeneralAgent()
evaluator = EvaluatorAgent()

def router_node(state): return router.process(state)
def rag_node(state): return rag.process(state)
def general_node(state): return general.process(state)
def evaluator_node(state): return evaluator.process(state)
def route_decision(state): return state.get("route", "rag")

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("rag_agent", rag_node)
    graph.add_node("general_agent", general_node)
    graph.add_node("evaluator", evaluator_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_decision, {"rag": "rag_agent", "general": "general_agent"})
    graph.add_edge("rag_agent", "evaluator")
    graph.add_edge("general_agent", "evaluator")
    graph.add_edge("evaluator", END)
    return graph.compile()

app = build_graph()