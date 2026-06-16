import streamlit as st
import requests
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Financial AI Platform",
    page_icon="📈",
    layout="wide"
)

# Session State
if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #1e293b
    );
}

.hero {
    text-align:center;
    padding:30px;
}

.hero h1{
    color:white;
    font-size:4rem;
}

.hero p{
    color:#94a3b8;
    font-size:1.2rem;
}

.glass{
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(15px);
    border-radius:20px;
    padding:20px;
    border:1px solid rgba(255,255,255,0.1);
}

.answer{
    background:rgba(0,255,150,0.08);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(0,255,150,0.2);
}

</style>
""", unsafe_allow_html=True)

def render_stats():
    try:
        stats = requests.get("http://127.0.0.1:8000/stats", timeout=5).json()
    except Exception:
        st.warning("Stats unavailable — make sure the API is running on port 8000.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", stats.get("total_companies", 0))
    c2.metric("Filings", stats.get("total_filings", 0))
    c3.metric("Chunks", stats.get("total_chunks", 0))
    c4.metric("Last updated", str(stats.get("last_updated", "—"))[:16])

# Sidebar
with st.sidebar:

    st.header("Question History")

    if len(st.session_state.history) == 0:
        st.write("No questions asked yet.")
    else:
        for q in reversed(st.session_state.history):
            st.write("•", q)

st.markdown("""
<div class="hero">
<h1>📈 Financial AI Platform</h1>
<p>SEC Filing Analysis using RAG + Llama 3 + pgvector</p>
</div>
""", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Ask AI", "System Stats"],
    icons=["robot", "bar-chart"],
    orientation="horizontal"
)

if selected == "Ask AI":

    render_stats()
    question = st.text_input(
        "Ask a financial question",
        placeholder="Who is the CEO?"
    )

    if st.button("Analyze"):

        if question:

            # Save question history
            st.session_state.history.append(question)

            with st.spinner(
                "Analyzing financial documents..."
            ):

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={
                        "question": question
                    }
                )

                answer = response.json()["answer"]

                st.markdown(
                    f"""
                    <div class="answer">
                    <h3>Answer</h3>
                    <p>{answer}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if selected == "System Stats":
    st.subheader("Live Knowledge Base")
    render_stats()
    st.subheader("RAG Architecture")
    st.code(
"""
SEC Filing
     ↓
Parser
     ↓
Chunking
     ↓
Embeddings
     ↓
pgvector
     ↓
Retriever
     ↓
Llama 3
     ↓
Answer
"""
    )

    st.success("Live data connected — pgvector + document_chunks")