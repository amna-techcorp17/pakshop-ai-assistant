from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class RecommendAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "RecommendAgent"

    def process(self, state: dict) -> dict:
        self.log("Generating recommendation...")
        needs = state.get('customer_needs', {})
        budget = needs.get('budget_amount')
        prompt = f"""You are a friendly Pakistani shopping assistant.
Customer Query: {state['query']}
Customer Budget: {f"Rs. {budget}" if budget else "Not specified"}
Search Results: {state.get('search_results', 'No data')}
Comparison: {state.get('comparison_result', 'No comparison')}
Give a warm helpful response in Urdu/English mix showing:
1. All platforms where product is available with prices
2. Best option for their budget (if given)
3. Delivery info
4. Offer to help further
Only use prices from search results."""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": response.content}
