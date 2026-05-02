# 🛍️ PakShop — AI Customer Assistant
> **A production-style Multi-Agent RAG System for a Pakistani E-Commerce Store, built with LangGraph, Groq, and FAISS.**

![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b--versatile-F55036?logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-VectorStore-0078D4)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📌 What is this?

PakShop AI Assistant is an **intelligent, multi-agent customer service chatbot** for a Pakistani e-commerce store. It uses **LangGraph** to orchestrate four specialized agents that handle product queries, shipping information, return policies, and general conversation — all powered by **Groq's LLM (`llama-3.3-70b-versatile`)**.

Every response is automatically evaluated by a dedicated `EvaluatorAgent` that scores quality on four dimensions: relevance, accuracy, friendliness, and completeness.

---

## 🧠 Agent Flow

```
User Query
    │
    ▼
┌─────────────┐
│ RouterAgent │  ← Classifies query as 'rag' or 'general'
└──────┬──────┘
       │
  ┌────┴────┐
  ▼          ▼
┌──────────┐  ┌────────────────┐
│ RAGAgent │  │ GeneralAgent   │
│(products,│  │(greetings,     │
│shipping, │  │ general chat)  │
│returns)  │  │                │
└────┬─────┘  └──────┬─────────┘
     │                │
     └───────┬─────────┘
             ▼
    ┌──────────────────┐
    │  EvaluatorAgent  │  ← Scores response quality (1–10)
    └────────┬─────────┘
             ▼
       Final Response → User
```

---

## 🤖 Agents

| Agent | Role | Design Pattern |
|-------|------|----------------|
| `RouterAgent` | Classifies query → `rag` or `general` | Chain of Responsibility |
| `RAGAgent` | Retrieves context from FAISS knowledge base | Strategy Pattern |
| `GeneralAgent` | Handles greetings & general conversation | Strategy Pattern |
| `EvaluatorAgent` | Scores response on 4 dimensions (1–10) | Observer Pattern |
| `BaseAgent` | Abstract base class for all agents | Template Method Pattern |

---

## 🎨 Design Patterns Implemented (5 Patterns)

| # | Pattern | Where Used | How |
|---|---------|-----------|-----|
| 1 | **Template Method** | `BaseAgent` | Defines abstract `process()` method all agents must implement |
| 2 | **Strategy** | `RAGAgent` & `GeneralAgent` | Interchangeable handlers selected by RouterAgent |
| 3 | **Singleton** | `RAGTool` | Only one FAISS vector store instance exists across the app |
| 4 | **Chain of Responsibility** | `RouterAgent` | Decides which agent owns the query |
| 5 | **Observer** | `EvaluatorAgent` | Observes and evaluates every response automatically |

---

## 🛍️ Business Scenario — PakShop E-Commerce Store

### Products Covered
| Category | Products |
|----------|---------|
| Electronics | Samsung Galaxy A54, iPhone 13, Xiaomi Redmi Note 12, HP Laptop 15s, JBL Bluetooth Speaker |
| Clothing | Men's Shalwar Kameez, Women's Lawn Suit (3-piece), Kids School Uniform, Casual Sneakers |
| Home Appliances | Dawlance Refrigerator, Orient AC 1.5 Ton, Anex Blender |

### Payment Methods
JazzCash · Easypaisa · Bank Transfer · Cash on Delivery (COD)

### Shipping
- **Major Cities** (Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad): 2–3 business days
- **Other Cities:** 4–6 business days
- **Remote Areas:** 7–10 business days
- **Free delivery** on orders above Rs. 5,000

### Return Policy
- 7-day return window from delivery date
- Refund processed in 5–7 business days
- COD refunds via JazzCash or Easypaisa

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Orchestration | LangGraph | Multi-agent graph pipeline |
| LLM | Groq — `llama-3.3-70b-versatile` | Fast language model inference |
| Embeddings | HuggingFace — `all-MiniLM-L6-v2` | Text vectorization |
| Vector Store | FAISS | Similarity search over knowledge base |
| UI | Streamlit | Interactive web chat interface |
| Language | Python 3.10+ | Core language |

---

## 📁 Project Structure

```
pakistan-ecom-assistant/
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base class (Template Method Pattern)
│   ├── router_agent.py        # Query classifier (Chain of Responsibility)
│   ├── rag_agent.py           # Knowledge retrieval agent (Strategy Pattern)
│   ├── general_agent.py       # Conversational agent (Strategy Pattern)
│   └── evaluator_agent.py     # Quality evaluator (Observer Pattern)
│
├── tools/
│   ├── __init__.py
│   └── rag_tool.py            # FAISS vector store wrapper (Singleton Pattern)
│
├── knowledge_base/
│   ├── products.txt           # Product catalog (Electronics, Clothing, Appliances)
│   ├── return_policy.txt      # Return & refund policy
│   └── shipping_info.txt      # Shipping areas, charges & courier partners
│
├── vector_store/              # Auto-generated FAISS index
├── graph.py                   # LangGraph StateGraph pipeline
├── main.py                    # Streamlit web application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## ⚙️ Quickstart

### Prerequisites
- Python 3.10+
- Free Groq API key → [console.groq.com](https://console.groq.com)

### Step 1 — Navigate to project folder
```bash
cd "pakistan-ecom-assistant"
```

### Step 2 — Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set Groq API Key
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

### Step 5 — Run the app
```bash
streamlit run main.py
```

---

## 🧪 Sample Queries to Test

| Query Type | Example |
|-----------|---------|
| 🛒 Product Price | `"iPhone 13 ki price kya hai?"` |
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