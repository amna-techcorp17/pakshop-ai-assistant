from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "RouterAgent"

    def process(self, state: dict) -> dict:
        self.log(f"Routing query: {state['query']}")
        prompt = f"""You are a router for a Pakistan e-commerce store assistant.
Classify this customer query into ONE category:
- rag: questions about products, prices, return policy, shipping, delivery
- general: greetings, thank you, general conversation

Query: {state['query']}

Respond with ONLY one word: either 'rag' or 'general'"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        route = response.content.strip().lower()
        if route not in ["rag", "general"]:
            route = "rag"
        self.log(f"Routed to: {route}")
        return {**state, "route": route}
