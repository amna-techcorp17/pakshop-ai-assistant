from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, List, Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.4
)

# ── ONLY these 3 platforms ──
ALLOWED_PLATFORMS = ["Daraz", "Telemart", "Homeshopping"]

PLATFORM_URLS = {
    "Daraz": "https://www.daraz.pk/catalog/?q=",
    "Telemart": "https://telemart.pk/search?q=",
    "Homeshopping": "https://homeshopping.pk/search?s="
}

class AgentState(TypedDict):
    user_message: str
    chat_history: List[Dict[str, str]]
    response: str
    platform_links: Optional[Dict[str, str]]
    platforms_searched: Optional[List[str]]
    intent: str
    is_first_message: bool
    user_id: Optional[str]

def build_messages(state: AgentState, system_prompt: str) -> list:
    """
    Build full message list with chat history for context continuity.
    This ensures agent remembers the FULL conversation.
    """
    messages = [SystemMessage(content=system_prompt)]
    
    # Add chat history so agent remembers previous messages
    history = state.get("chat_history", [])
    for msg in history[:-1]:  # All except the last (current) message
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Add current user message
    messages.append(HumanMessage(content=state["user_message"]))
    return messages

def router_agent(state: AgentState) -> AgentState:
    """Determines the intent of the user's message."""
    
    system = """You are a router for a Pakistan shopping assistant. 
    Classify the user's intent into ONE of these categories:
    - product_search: user wants to find/buy a product
    - price_compare: user wants to compare prices
    - recommendation: user wants recommendations
    - general: general question or greeting
    
    Respond ONLY with the category word, nothing else."""
    
    msgs = build_messages(state, system)
    result = llm.invoke(msgs)
    intent = result.content.strip().lower()
    
    valid_intents = ["product_search", "price_compare", "recommendation", "general"]
    if intent not in valid_intents:
        intent = "general"
    
    return {**state, "intent": intent}

def search_agent(state: AgentState) -> AgentState:
    """Handles product search with full conversation context."""
    
    is_first = state.get("is_first_message", False)
    
    # Only greet on VERY FIRST message of the session
    greeting_instruction = ""
    if is_first:
        greeting_instruction = "Start with a brief friendly greeting in Urdu/English."
    else:
        greeting_instruction = "DO NOT greet. Continue the conversation naturally. Remember the previous messages."
    
    system = f"""You are PakShop AI — Pakistan's smart shopping assistant.
You help users find products on Daraz, Telemart, and Homeshopping ONLY.
NEVER mention PriceOye, Mega.pk, iShopping, Symbios, or any other platform.

{greeting_instruction}

Rules:
- Answer in the SAME language the user used (Urdu or English)
- If user asked a follow-up question, relate it to previous conversation
- Provide helpful product info, prices (PKR), specs
- Be concise — max 4-5 sentences
- Mention only Daraz, Telemart, Homeshopping
- Do NOT add "Thanks for choosing..." at the end"""
    
    msgs = build_messages(state, system)
    result = llm.invoke(msgs)
    
    # Generate search URLs for the 3 platforms
    query = state["user_message"]
    import urllib.parse
    encoded = urllib.parse.quote(query)
    
    platform_links = {
        "Daraz": f"{PLATFORM_URLS['Daraz']}{encoded}",
        "Telemart": f"{PLATFORM_URLS['Telemart']}{encoded}",
        "Homeshopping": f"{PLATFORM_URLS['Homeshopping']}{encoded}"
    }
    
    return {
        **state,
        "response": result.content.strip(),
        "platform_links": platform_links,
        "platforms_searched": ALLOWED_PLATFORMS
    }

def recommendation_agent(state: AgentState) -> AgentState:
    """Gives product recommendations with full context."""
    
    is_first = state.get("is_first_message", False)
    greeting_instruction = "DO NOT greet again." if not is_first else "Start with a brief greeting."
    
    system = f"""You are PakShop AI — Pakistan's smart shopping assistant.
{greeting_instruction}

Give specific product recommendations for Pakistan market.
ONLY mention Daraz, Telemart, Homeshopping — NEVER any other platform.
Answer in user's language (Urdu or English).
Remember the conversation history and continue naturally.
Format: product name, key specs, approximate price in PKR.
Max 3 recommendations. Be concise."""
    
    msgs = build_messages(state, system)
    result = llm.invoke(msgs)
    
    query = state["user_message"]
    import urllib.parse
    encoded = urllib.parse.quote(query)
    
    platform_links = {
        "Daraz": f"{PLATFORM_URLS['Daraz']}{encoded}",
        "Telemart": f"{PLATFORM_URLS['Telemart']}{encoded}",
        "Homeshopping": f"{PLATFORM_URLS['Homeshopping']}{encoded}"
    }
    
    return {
        **state,
        "response": result.content.strip(),
        "platform_links": platform_links,
        "platforms_searched": ALLOWED_PLATFORMS
    }

def comparison_agent(state: AgentState) -> AgentState:
    """Compares prices across Daraz, Telemart, Homeshopping only."""
    
    is_first = state.get("is_first_message", False)
    greeting_instruction = "DO NOT greet again." if not is_first else "Start with a brief greeting."
    
    system = f"""You are PakShop AI — Pakistan's price comparison assistant.
{greeting_instruction}

Compare prices ONLY across: Daraz, Telemart, Homeshopping.
NEVER mention PriceOye, Mega.pk, iShopping, Symbios, or others.
Answer in user's language (Urdu or English).
Remember conversation context.
Provide estimated price ranges for Pakistan in PKR."""
    
    msgs = build_messages(state, system)
    result = llm.invoke(msgs)
    
    query = state["user_message"]
    import urllib.parse
    encoded = urllib.parse.quote(query)
    
    platform_links = {
        "Daraz": f"{PLATFORM_URLS['Daraz']}{encoded}",
        "Telemart": f"{PLATFORM_URLS['Telemart']}{encoded}",
        "Homeshopping": f"{PLATFORM_URLS['Homeshopping']}{encoded}"
    }
    
    return {
        **state,
        "response": result.content.strip(),
        "platform_links": platform_links,
        "platforms_searched": ALLOWED_PLATFORMS
    }

def general_agent(state: AgentState) -> AgentState:
    """Handles general queries with conversation continuity."""
    
    is_first = state.get("is_first_message", False)
    greeting_instruction = "DO NOT greet again. Continue naturally." if not is_first else "You may greet the user once briefly."
    
    system = f"""You are PakShop AI — Pakistan's smart shopping assistant.
{greeting_instruction}

Answer general questions helpfully.
Remember the full conversation — never treat user as a new person.
Answer in user's language (Urdu or English).
Keep it short and friendly."""
    
    msgs = build_messages(state, system)
    result = llm.invoke(msgs)
    
    return {
        **state,
        "response": result.content.strip(),
        "platform_links": None,
        "platforms_searched": []
    }

def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "general")
    if intent == "product_search":
        return "search"
    elif intent == "recommendation":
        return "recommend"
    elif intent == "price_compare":
        return "compare"
    else:
        return "general"

# Build the graph
def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("router", router_agent)
    graph.add_node("search", search_agent)
    graph.add_node("recommend", recommendation_agent)
    graph.add_node("compare", comparison_agent)
    graph.add_node("general", general_agent)
    
    graph.set_entry_point("router")
    
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "search": "search",
            "recommend": "recommend",
            "compare": "compare",
            "general": "general"
        }
    )
    
    graph.add_edge("search", END)
    graph.add_edge("recommend", END)
    graph.add_edge("compare", END)
    graph.add_edge("general", END)
    
    return graph.compile()

# Compiled graph — import this in app.py
agent_graph = build_graph()

def run_agent(
    user_message: str,
    chat_history: list = None,
    is_first_message: bool = False,
    user_id: str = None
) -> dict:
    """
    Main function to run the agent.
    chat_history: list of {role, content} dicts — full conversation
    is_first_message: True only for the very first message of session
    user_id: email or id to track user
    """
    state = AgentState(
        user_message=user_message,
        chat_history=chat_history or [],
        response="",
        platform_links=None,
        platforms_searched=[],
        intent="general",
        is_first_message=is_first_message,
        user_id=user_id
    )
    
    result = agent_graph.invoke(state)
    
    return {
        "response": result.get("response", ""),
        "platform_links": result.get("platform_links"),
        "platforms_searched": result.get("platforms_searched", [])
    }