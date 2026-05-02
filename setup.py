import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Created: {path}")

write_file("agents/router_agent.py", """from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "RouterAgent"

    def process(self, state: dict) -> dict:
        self.log(f"Routing query: {state['query']}")
        prompt = f\"\"\"You are a router for a Pakistan e-commerce store assistant.
Classify this customer query into ONE category:
- rag: questions about products, prices, return policy, shipping, delivery
- general: greetings, thank you, general conversation

Query: {state['query']}

Respond with ONLY one word: either 'rag' or 'general'\"\"\"

        response = self.llm.invoke([HumanMessage(content=prompt)])
        route = response.content.strip().lower()
        if route not in ["rag", "general"]:
            route = "rag"
        self.log(f"Routed to: {route}")
        return {**state, "route": route}
""")

write_file("agents/rag_agent.py", """from agents.base_agent import BaseAgent
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
        prompt = f\"\"\"You are a helpful customer service agent for a Pakistani e-commerce store.
Use the following context to answer the customer's question accurately.

Context:
{context}

Customer Question: {state['query']}

Provide a helpful, accurate answer:\"\"\"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": response.content, "context": context}
""")

write_file("agents/general_agent.py", """from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "GeneralAgent"

    def process(self, state: dict) -> dict:
        self.log(f"Processing general query: {state['query']}")
        prompt = f\"\"\"You are a friendly customer service agent for a Pakistani e-commerce store called PakShop.
Handle this general conversation naturally and warmly.
You can use Urdu/English mix if appropriate.

Customer message: {state['query']}

Respond naturally:\"\"\"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {**state, "response": response.content, "context": ""}
""")

write_file("agents/evaluator_agent.py", """from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage
import json
import re

class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "EvaluatorAgent"

    def process(self, state: dict) -> dict:
        self.log("Evaluating response quality...")
        prompt = f\"\"\"Evaluate this customer service response.

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
}}\"\"\"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        try:
            json_match = re.search(r'\\{.*\\}', response.content, re.DOTALL)
            evaluation = json.loads(json_match.group()) if json_match else {"overall": 7, "feedback": "OK"}
        except:
            evaluation = {"overall": 7, "feedback": "Evaluation error"}
        self.log(f"Score: {evaluation.get('overall', 'N/A')}")
        return {**state, "evaluation": evaluation}
""")

write_file("tools/rag_tool.py", """from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os

class RAGTool:
    _instance = None
    _vectorstore = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._vectorstore is None:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self._build_vectorstore()

    def _build_vectorstore(self):
        print("[RAGTool] Building vector store...")
        documents = []
        for filename in os.listdir("knowledge_base"):
            if filename.endswith(".txt"):
                loader = TextLoader(os.path.join("knowledge_base", filename), encoding="utf-8")
                documents.extend(loader.load())
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        RAGTool._vectorstore = FAISS.from_documents(chunks, self.embeddings)
        print("[RAGTool] Vector store ready!")

    def retrieve(self, query: str, k: int = 3) -> str:
        docs = RAGTool._vectorstore.similarity_search(query, k=k)
        return "\\n\\n".join([doc.page_content for doc in docs])
""")

write_file("graph.py", """from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.router_agent import RouterAgent
from agents.rag_agent import RAGAgent
from agents.general_agent import GeneralAgent
from agents.evaluator_agent import EvaluatorAgent

class AgentState(TypedDict):
    query: str
    route: Optional[str]
    response: Optional[str]
    context: Optional[str]
    evaluation: Optional[dict]

router = RouterAgent()
rag = RAGAgent()
general = GeneralAgent()
evaluator = EvaluatorAgent()

def router_node(state): return router.process(state)
def rag_node(state): return rag.process(state)
def general_node(state): return general.process(state)
def evaluator_node(state): return evaluator.process(state)
def route_decision(state): return state.get("route", "rag")

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("rag_agent", rag_node)
    graph.add_node("general_agent", general_node)
    graph.add_node("evaluator", evaluator_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_decision, {"rag": "rag_agent", "general": "general_agent"})
    graph.add_edge("rag_agent", "evaluator")
    graph.add_edge("general_agent", "evaluator")
    graph.add_edge("evaluator", END)
    return graph.compile()

app = build_graph()
""")

write_file("main.py", """import streamlit as st
from graph import app

st.set_page_config(page_title="PakShop Assistant", page_icon="🛍️", layout="centered")
st.title("🛍️ PakShop - AI Customer Assistant")
st.markdown("*Powered by LangGraph + Groq*")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if query := st.chat_input("Apna sawal poochein..."):
    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hun..."):
            result = app.invoke({"query": query, "route": None, "response": None, "context": None, "evaluation": None})
        st.write(result["response"])

        if result.get("evaluation"):
            with st.expander("📊 Response Quality Score"):
                eval_data = result["evaluation"]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Relevance", f"{eval_data.get('relevance', 'N/A')}/10")
                col2.metric("Accuracy", f"{eval_data.get('accuracy', 'N/A')}/10")
                col3.metric("Friendliness", f"{eval_data.get('friendliness', 'N/A')}/10")
                col4.metric("Overall", f"{eval_data.get('overall', 'N/A')}/10")
                st.info(f"💬 {eval_data.get('feedback', '')}")
        st.caption(f"🔀 Routed to: {result.get('route', 'N/A').upper()} Agent")

    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
""")

print("All files created successfully!")