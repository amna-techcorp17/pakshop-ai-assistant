from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage
import json
import re

class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "EvaluatorAgent"

    def process(self, state: dict) -> dict:
        self.log("Evaluating response quality...")
        prompt = f"""Evaluate this customer service response.

Customer Query: {state['query']}
Agent Response: {state['response']}

Respond ONLY with this JSON:
{{
    "relevance": 8,
    "accuracy": 9,
    "friendliness": 8,
    "completeness": 7,
    "overall": 8,
    "feedback": "Good response."
}}"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            evaluation = json.loads(json_match.group()) if json_match else {"overall": 7, "feedback": "OK"}
        except:
            evaluation = {"overall": 7, "feedback": "Evaluation error"}
        self.log(f"Score: {evaluation.get('overall', 'N/A')}")
        return {**state, "evaluation": evaluation}
