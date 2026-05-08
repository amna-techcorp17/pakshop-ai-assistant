from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class RouterAgent(BaseAgent):
    """Routes queries to appropriate pipeline"""
    
    def __init__(self):
        super().__init__()
        self.agent_name = "RouterAgent"
    
    def process(self, state: dict) -> dict:
        self.log(f"Routing query: {state['query']}")
        
        prompt = f"""You are a router for a Pakistani shopping assistant.

Classify this customer query into ONE category:
- "search": anything related to products, shopping, prices, buying, comparing, platforms, delivery, availability, brands
- "general": greetings, thank you, general conversation, help questions not related to shopping

Query: {state['query']}

Respond with ONLY one word: either 'search' or 'general'"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        route = response.content.strip().lower()
        
        if route not in ["search", "general"]:
            route = "search"
        
        self.log(f"Routed to: {route}")
        
        return {
            **state,
            "route": route
        }