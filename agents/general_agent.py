from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class GeneralAgent(BaseAgent):
    """Handles general conversation"""
    
    def __init__(self):
        super().__init__()
        self.agent_name = "GeneralAgent"
    
    def process(self, state: dict) -> dict:
        self.log(f"Processing general query: {state['query']}")
        
        prompt = f"""You are a friendly shopping assistant called "Pak-Commerce AI Assistant" for Pakistani online shoppers.

Handle this general conversation naturally and warmly.
Use a mix of English and Urdu (Roman) to feel natural for Pakistani users.
Always guide customers to ask about products, prices, or platform comparisons.

You can help with:
- Finding products on Pakistani platforms (Daraz, Telemart, Homeshopping, iShopping, Symbios)
- Comparing prices across platforms
- Budget-based recommendations
- Delivery and shipping queries

Customer message: {state['query']}

Respond naturally and helpfully:"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            **state,
            "response": response.content
        }