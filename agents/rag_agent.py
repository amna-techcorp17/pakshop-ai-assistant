from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class RAGAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "RAGAgent"

    def process(self, state: dict) -> dict:
        return state