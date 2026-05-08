from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
from agents.router_agent import RouterAgent
from agents.search_agent import SearchAgent
from agents.needs_agent import NeedsAgent
from agents.comparison_agent import ComparisonAgent
from agents.recommend_agent import RecommendAgent
from agents.general_agent import GeneralAgent
from agents.evaluator_agent import EvaluatorAgent

class AgentState(TypedDict):
    query: str
    route: Optional[str]
    search_results: Optional[str]
    platforms_searched: Optional[List[str]]
    platform_links: Optional[Dict[str, str]]
    customer_needs: Optional[dict]
    comparison_result: Optional[str]
    response: Optional[str]
    evaluation: Optional[dict]

router = RouterAgent()
search = SearchAgent()
needs = NeedsAgent()
comparison = ComparisonAgent()
recommend = RecommendAgent()
general = GeneralAgent()
evaluator = EvaluatorAgent()

def router_node(state): return router.process(state)
def search_node(state): return search.process(state)
def needs_node(state): return needs.process(state)
def comparison_node(state): return comparison.process(state)
def recommend_node(state): return recommend.process(state)
def general_node(state): return general.process(state)
def evaluator_node(state): return evaluator.process(state)
def route_decision(state): return state.get("route", "search")

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("needs", needs_node)
    graph.add_node("comparison", comparison_node)
    graph.add_node("recommend", recommend_node)
    graph.add_node("general", general_node)
    graph.add_node("evaluator", evaluator_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_decision, {"search": "search", "general": "general"})
    graph.add_edge("search", "needs")
    graph.add_edge("needs", "comparison")
    graph.add_edge("comparison", "recommend")
    graph.add_edge("recommend", "evaluator")
    graph.add_edge("general", "evaluator")
    graph.add_edge("evaluator", END)
    return graph.compile()

app = build_graph()