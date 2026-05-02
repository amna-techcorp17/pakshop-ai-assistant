from abc import ABC, abstractmethod
from langchain_groq import ChatGroq
import os

class BaseAgent(ABC):
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name=model_name)
        self.agent_name = self.__class__.__name__

    @abstractmethod
    def process(self, state: dict) -> dict:
        pass

    def log(self, message: str):
        print(f"[{self.agent_name}] {message}")