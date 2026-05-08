from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage
import json, re

class NeedsAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "NeedsAgent"

    def process(self, state: dict) -> dict:
        self.log("Analyzing customer needs...")
        prompt = f"""Analyze this customer query and extract needs.
Customer Query: {state['query']}
Respond ONLY with this JSON:
{{
    "product_identified": "product name or not clear",
    "budget_mentioned": true or false,
    "budget_amount": 150000 or null,
    "specific_requirements": [],
    "needs_more_info": false,
    "question_to_ask": null,
    "summary": "brief summary"
}}"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            needs = json.loads(json_match.group()) if json_match else {}
        except:
            needs = {"needs_more_info": False, "summary": state['query']}
        return {**state, "customer_needs": needs}
