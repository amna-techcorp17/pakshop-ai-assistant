from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class ComparisonAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "ComparisonAgent"

    def process(self, state: dict) -> dict:
        self.log("Comparing products...")
        budget = state.get('customer_needs', {}).get('budget_amount')
        budget_str = f"Rs. {budget}" if budget else "No budget specified"
        prompt = f"""Compare these search results for Pakistani e-commerce platforms.
Search Results: {state.get('search_results', 'No results')}
Customer Budget: {budget_str}
Rank options best to worst. Format:
COMPARISON RESULTS
#1 BEST VALUE
Platform: [name]
Price: Rs. [price]
Within Budget: Yes/No
Why Best: [reason]
---
RECOMMENDATION: [final recommendation]"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "comparison_result": response.content}
