from agents.base_agent import BaseAgent
from tools.rag_tool import RAGTool
from langchain_core.messages import HumanMessage

class RAGAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "RAGAgent"
        self.rag_tool = RAGTool()

    def process(self, state: dict) -> dict:
        self.log(f"Processing query: {state['query']}")
        context = self.rag_tool.retrieve(state['query'])
        prompt = f"""You are a helpful customer service agent for a Pakistani e-commerce store.
Use the following context to answer the customer's question accurately.

Context:
{context}

Customer Question: {state['query']}

Provide a helpful, accurate answer:"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": response.content, "context": context}
