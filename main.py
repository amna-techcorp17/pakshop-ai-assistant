import streamlit as st
from graph import app
import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_name TEXT,
                  created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  role TEXT,
                  content TEXT,
                  platform_links TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def create_session(name):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    keywords = ' '.join(name.split()[:3]) + '...'
    c.execute("INSERT INTO sessions (session_name, created_at) VALUES (?, ?)",
              (keywords, datetime.now().strftime("%Y-%m-%d %H:%M")))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_sessions():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT id, session_name, created_at FROM sessions ORDER BY id DESC")
    sessions = c.fetchall()
    conn.close()
    return sessions

def save_message(session_id, role, content, platform_links=None):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, platform_links, timestamp) VALUES (?, ?, ?, ?, ?)",
              (session_id, role, content, json.dumps(platform_links) if platform_links else None,
               datetime.now().strftime("%H:%M")))
    conn.commit()
    conn.close()

def load_messages(session_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role, content, platform_links FROM messages WHERE session_id=? ORDER BY id",
              (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_session(session_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

init_db()

st.set_page_config(
    page_title="Pak-Commerce AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Hide streamlit defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #667eea !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="collapsedControl"] {display: flex !important;}

/* Main background */
.stApp {
    background: #0f0f1a !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1a2e !important;
    border-right: 1px solid #2a2a4a !important;
    min-width: 200px !important;
    max-width: 200px !important;
}

section[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

/* Sidebar padding */
section[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.8rem !important;
}

/* Buttons in sidebar */
section[data-testid="stSidebar"] .stButton button {
    background: #2a2a4a !important;
    color: #e0e0e0 !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    padding: 4px 8px !important;
    margin: 2px 0 !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #667eea33 !important;
    border-color: #667eea !important;
}

/* Main content */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 900px !important;
}

/* Suggestion buttons */
div[data-testid="column"] .stButton button {
    background: #1e1e3a !important;
    color: #a0a8d0 !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}

div[data-testid="column"] .stButton button:hover {
    background: #667eea22 !important;
    border-color: #667eea !important;
    color: #ffffff !important;
}

/* Chat messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 8px 0 !important;
}

/* User message bubble */
[data-testid="stChatMessageContent"] {
    background: #1e1e3a !important;
    border-radius: 12px !important;
    border: 1px solid #2a2a4a !important;
    padding: 12px 16px !important;
    color: #e0e0e0 !important;
}

/* Chat input */
.stChatInput {
    background: #1a1a2e !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 12px !important;
}

.stChatInput textarea {
    background: #1a1a2e !important;
    color: #e0e0e0 !important;
    font-size: 14px !important;
}

/* Divider */
hr {
    border-color: #2a2a4a !important;
    margin: 8px 0 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1e1e3a !important;
    border-radius: 8px !important;
    color: #a0a8d0 !important;
}
</style>
""", unsafe_allow_html=True)

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_first_message" not in st.session_state:
    st.session_state.is_first_message = True
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar
with st.sidebar:
    st.markdown("### 🛍️ Pak-Commerce AI")
    st.markdown("---")

    if st.button("➕ New Chat", key="new_chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.session_state.is_first_message = True
        st.rerun()

    st.markdown("**💬 History**")

    sessions = get_sessions()
    for session in sessions:
        sid, sname, created = session
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"🗨 {sname}", key=f"sess_{sid}", use_container_width=True):
                st.session_state.current_session_id = sid
                rows = load_messages(sid)
                st.session_state.messages = [
                    {"role": r[0], "content": r[1],
                     "platform_links": json.loads(r[2]) if r[2] else None}
                    for r in rows
                ]
                st.session_state.is_first_message = False
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{sid}"):
                delete_session(sid)
                if st.session_state.get("current_session_id") == sid:
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                    st.session_state.is_first_message = True
                st.rerun()

    st.markdown("---")
st.markdown("<p style='color: #555; font-size: 11px; text-align: center;'>Powered by LangGraph + Groq</p>", unsafe_allow_html=True)

# Main header
st.markdown("""
<div style='margin-bottom: 8px;'>
    <span style='font-size: 28px; font-weight: 700; background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🛍️ Pakistan's Online Shopping Assistant
    </span>
</div>
<p style='color: #8892b0; font-size: 13px; margin-top: -4px;'>
    Real-time prices from Daraz • Telemart • Homeshopping
</p>
""", unsafe_allow_html=True)
st.markdown("---")

suggestions = [
    "Compare iPhone prices across all platforms",
    "Find best laptop under Rs. 50,000",
    "Which platform has the cheapest Samsung Galaxy?"
]
for i, sug in enumerate(suggestions):
    if st.button(sug, key=f"sug_{i}", use_container_width=True):
        st.session_state.selected_query = sug

st.markdown("""
<div style='background: #1e1e3a; border: 1px solid #3a3a6a; border-radius: 12px; 
padding: 10px 16px; color: #8892b0; font-size: 13px; text-align: center; margin-top: 4px;'>
💬 Aap apni national language mein bhi sawal kar saktay hain
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and message.get("platform_links"):
            with st.expander("🔗 Direct Links"):
                for platform, link in message["platform_links"].items():
                    st.markdown(f"- [{platform}]({link})")

# Handle input
if "selected_query" in st.session_state:
    query = st.session_state.selected_query
    del st.session_state.selected_query
else:
    query = None

user_input = st.chat_input("What are you looking for today?")
if user_input:
    query = user_input

if query:
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = create_session(query)
        st.session_state.is_first_message = True

    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})
    save_message(st.session_state.current_session_id, "user", query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving from all available platforms..."):
            result = app.invoke({
                "query": query,
                "route": None,
                "search_results": None,
                "platforms_searched": None,
                "platform_links": None,
                "customer_needs": None,
                "comparison_result": None,
                "response": None,
                "evaluation": None
            })

        response_text = result["response"]

        if st.session_state.is_first_message:
            if "assalam" not in response_text.lower():
                response_text = "Assalam-o-Alaikum! 👋\n\n" + response_text
            st.session_state.is_first_message = False

        response_text = response_text + "\n\n---\n*Thanks for choosing Pak-Commerce AI! Wish you a happy shopping ✨ — come back anytime! 💫*"

        st.write(response_text)

        if result.get("platform_links"):
            with st.expander("🔗 Direct Links"):
                for platform, link in result["platform_links"].items():
                    st.markdown(f"- [{platform}]({link})")

        st.caption(f"🔍 {', '.join(result.get('platforms_searched', []))}")

    save_message(st.session_state.current_session_id, "assistant", response_text, result.get("platform_links"))
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "platform_links": result.get("platform_links")
    })