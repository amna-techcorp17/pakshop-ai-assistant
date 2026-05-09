# 🛍️ PakShop — AI Customer Assistant
> **A production-style Multi-Agent RAG System for a Pakistani E-Commerce Store, built with LangGraph, Groq, and FAISS.**

![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b--versatile-F55036?logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-VectorStore-0078D4)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📌 Project Overview

**PakShop AI Assistant** is a production-style, multi-agent AI shopping chatbot built for Pakistani e-commerce. It searches real platforms (Daraz, Telemart, Homeshopping), analyzes customer needs, compares products, and delivers smart recommendations — all powered by **Groq's llama-3.3-70b-versatile** LLM orchestrated through **LangGraph**.

The system features full **JWT-based user authentication**, **persistent chat history** per user via SQLite, and an **EvaluatorAgent** that automatically scores every response on relevance, accuracy, friendliness, and completeness.

---



## 🧠 Agent Flow

User Query
│
▼
┌─────────────┐
│ RouterAgent │  ← Classifies: 'search' or 'general'
└──────┬──────┘
│
┌────┴────┐
▼          ▼
SearchAgent  GeneralAgent
│
▼
NeedsAgent        ← Extracts customer requirements
│
▼
ComparisonAgent   ← Compares shortlisted products
│
▼
RecommendAgent    ← Picks best match with reasoning
│
└──────────────┐
▼
┌──────────────────┐
│  EvaluatorAgent  │  ← Auto-scores response (1–10)
└────────┬─────────┘
▼
Final Response → User

---

## 🤖 Agent Breakdown

| Agent | File | Role | Design Pattern |
|---|---|---|---|
| RouterAgent | agents/router_agent.py | Classifies query as 'search' or 'general' | Chain of Responsibility |
| SearchAgent | agents/search_agent.py | Searches Daraz, Telemart, Homeshopping | Strategy Pattern |
| NeedsAgent | agents/needs_agent.py | Extracts and analyzes customer requirements | Strategy Pattern |
| ComparisonAgent | agents/comparison_agent.py | Compares shortlisted products side by side | Strategy Pattern |
| RecommendAgent | agents/recommend_agent.py | Picks best product and explains why | Strategy Pattern |
| GeneralAgent | agents/general_agent.py | Handles greetings and general conversation | Strategy Pattern |
| EvaluatorAgent | agents/evaluator_agent.py | Scores response on 4 quality metrics | Observer Pattern |
| BaseAgent | agents/base_agent.py | Abstract base — enforces process() interface | Template Method Pattern |

---

## 🎨 Design Patterns (5 Implemented)

| # | Pattern | Where Used | How |
|---|---|---|---|
| 1 | Template Method | BaseAgent | Abstract process() method all agents must implement |
| 2 | Strategy | SearchAgent, NeedsAgent, ComparisonAgent, RecommendAgent, GeneralAgent | Swappable handlers chosen at runtime by RouterAgent |
| 3 | Singleton | RAGTool (tools/rag_tool.py) | Single shared FAISS vector store instance |
| 4 | Chain of Responsibility | RouterAgent | Decides which pipeline owns the query |
| 5 | Observer | EvaluatorAgent | Observes and evaluates every response automatically |

---

## 🛒 Platforms Searched (Real-time)

| Platform | Coverage |
|---|---|
| Daraz.pk | Electronics, clothing, appliances, accessories |
| Telemart.pk | Electronics and gadgets |
| Homeshopping.pk | Home appliances and general products |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Orchestration | LangGraph (StateGraph) | Multi-agent graph pipeline |
| LLM | Groq — llama-3.3-70b-versatile | Fast language model inference |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 | Semantic text vectorization |
| Vector Store | FAISS | Similarity search over knowledge base |
| UI | Streamlit | Dark-themed interactive web chat |
| Authentication | JWT (python-jose) + bcrypt (passlib) | Secure user login and registration |
| Database | SQLite — chat_history.db + pakcommerce.db | Per-user session and message persistence |
| Language | Python 3.10+ | Core language |

---

---

## 🔐 Authentication System (auth.py)

The project includes a full user auth system:

- User registration with bcrypt password hashing
- Login with email and password verification
- JWT tokens (HS256) with 30-day expiry
- Per-user session creation, loading, and deletion
- All data stored in pakcommerce.db (SQLite)

---

## ⚙️ Quickstart

### Prerequisites

- Python 3.10+
- Free Groq API key from https://console.groq.com

### Step 1 — Clone the repository
git clone https://github.com/amna-techcorp17/pakshop-ai-assistant.git
cd pakshop-ai-assistant

### Step 2 — Create and activate virtual environment
python -m venv venv
Windows
venv\Scripts\activate
Mac / Linux
source venv/bin/activate

### Step 3 — Install dependencies
pip install -r requirements.txt

### Step 4 — Set your Groq API Key
Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"
Mac / Linux
export GROQ_API_KEY="your_groq_api_key_here"

### Step 5 — Run the app
streamlit run main.py
Open your browser at http://localhost:8501

---

## 🧪 Sample Queries to Test

| Query Type | Example |
|---|---|
| Price Search | "iPhone 13 ki price kya hai?" |
| Platform Compare | "Compare iPhone prices across all platforms" |
| Budget Search | "Find best laptop under Rs. 50,000" |
| Best Deal | "Which platform has cheapest Samsung Galaxy?" |
| Shipping Query | "Lahore mein delivery kitne din mein hogi?" |
| Returns | "Main product return karna chahta hun" |
| Payment | "Kya COD available hai?" |
| General | "Assalam-o-Alaikum!" |

---

## 📊 Automated Evaluation (EvaluatorAgent)

Every response is auto-scored on:

| Metric | Description |
|---|---|
| Relevance | Is the answer on-topic for the query? |
| Accuracy | Is information correct per the knowledge base? |
| Friendliness | Is tone warm and customer-friendly? |
| Completeness | Does it fully address the query? |
| Overall | Composite score out of 10 |

---

## 🔑 Key Features

- Multi-Agent Pipeline — 7 specialized agents in a sequential LangGraph graph
- Real Platform Search — Daraz, Telemart, Homeshopping live search
- JWT Authentication — Secure register/login with bcrypt + python-jose
- Persistent Chat History — Per-user SQLite session storage
- Bilingual Support — Handles Urdu, Roman Urdu, and English
- Auto Response Evaluation — Every reply scored on 4 quality dimensions
- 5 OOP Design Patterns — Production-grade software architecture
- Dark UI — Custom Streamlit dark theme with gradient branding

---

## 📦 Dependencies

langgraph
langchain
langchain-groq
langchain-community
faiss-cpu
python-dotenv
streamlit
pypdf
sentence-transformers
python-jose
passlib[bcrypt]


## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Orchestration | LangGraph | Multi-agent graph pipeline |
| LLM | Groq — `llama-3.3-70b-versatile` | Fast language model inference |
| Embeddings | HuggingFace — `all-MiniLM-L6-v2` | Text vectorization |
| Vector Store | FAISS | Similarity search over knowledge base |
| Language | Python 3.10+ | Core language |

---

## 📁 Project Structure

pakshop-ai-assistant/
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── router_agent.py
│   ├── search_agent.py
│   ├── needs_agent.py
│   ├── comparison_agent.py
│   ├── recommend_agent.py
│   ├── general_agent.py
│   └── evaluator_agent.py
│
├── tools/
│   ├── __init__.py
│   └── rag_tool.py
│
├── static/
│   └── (CSS, images, assets)
│
├── graph.py
├── main.py
├── auth.py
├── app.py
├── index.py
├── setup.py
├── index.html
├── chat_history.db
├── pakcommerce.db
├── .gitignore
└── README.md


```



## 🧪 Sample Queries to Test

| Query Type | Example |
|-----------|---------|
| 🛒 Product Price | `"iPhone 13 ki price kya hai sab platforms pe?"` |
| 🚚 Shipping | `"Lahore mein delivery kitne din mein hogi?"` |
| 🔄 Returns | `"Main product return karna chahta hun"` |
| 💳 Payment | `"Kya COD available hai?"` |
| 📦 Stock | `"Samsung Galaxy A54 available hai?"` |
| 👋 General | `"Assalam-o-Alaikum!"` |

---

## 📊 Evaluation Metrics

Every response is automatically scored by `EvaluatorAgent` on:

| Metric | Description |
|--------|-------------|
| **Relevance** | Is the answer relevant to the customer's query? |
| **Accuracy** | Is the information factually correct per the knowledge base? |
| **Friendliness** | Is the tone warm, professional, and customer-friendly? |
| **Completeness** | Does it fully address all parts of the query? |
| **Overall** | Composite score out of 10 |

---

## 📦 Requirements

```
langgraph
langchain
langchain-groq
langchain-community
faiss-cpu
python-dotenv
streamlit
pypdf
sentence-transformers
```

---

## 👩‍💻 Developer

| | |
|--|--|
| **Name** | Amna |
| **Course** | Artificial Intelligence |
| **Project** | Final Project — Multi-Agent Agentic RAG System |
| **Stack** | LangGraph + Groq + FAISS + Streamlit |
| **Date** | May 2026 |

---

## 📄 License

MIT — use, share, remix freely.
