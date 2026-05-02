from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "GeneralAgent"

    def process(self, state: dict) -> dict:
        self.log(f"Processing general query: {state['query']}")
        prompt = f"""You are a friendly customer service agent for a Pakistani e-commerce store called PakShop.
Handle this general conversation naturally and warmly.
You can use Urdu/English mix if appropriate.

Customer message: {state['query']}

Respond naturally:"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": response.content, "context": ""}
