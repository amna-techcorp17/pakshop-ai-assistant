import streamlit as st
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
