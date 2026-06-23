import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
load_dotenv()

from vectorstore.stats import get_stats
from vectorstore.database import get_connection
from rag.retriever import retrieve_context
from rag.chain import ask_question

st.set_page_config(
    page_title="Financial AI Platform",
    page_icon="📈",
    layout="wide"
)

if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
}
/* All text light by default */
.stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stMarkdown {
    color: #e2e8f0 !important;
}
/* Hero title */
.hero { text-align:center; padding:30px; }
.hero h1 { color:#ffffff !important; font-size:3.5rem; margin:0; }
.hero p { color:#00d4aa !important; font-size:1.2rem; margin-top:10px; }

/* Metric tiles */
[data-testid="stMetricLabel"] {
    color:#94a3b8 !important;
    font-size:0.9rem !important;
}
[data-testid="stMetricValue"] {
    color:#00d4aa !important;
    font-weight:600 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:#060d1a !important;
}
section[data-testid="stSidebar"] * {
    color:#cbd5e1 !important;
}

/* Text input */
.stTextInput input {
    background-color:#0d1f3c !important;
    color:#e2e8f0 !important;
    border:1px solid #1e3a5f !important;
}

/* Analyze button — green */
.stButton > button {
    background:linear-gradient(135deg, #00d4aa, #00b894) !important;
    color:#020617 !important;
    font-weight:600 !important;
    border:none !important;
    padding:8px 30px !important;
    border-radius:8px !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg, #00e6bb, #00d4aa) !important;
    box-shadow:0 4px 15px rgba(0,212,170,0.4) !important;
}

/* Answer card — green accent */
.answer {
    background:rgba(0,212,170,0.08);
    padding:24px;
    border-radius:15px;
    border:1px solid rgba(0,212,170,0.3);
    border-left:4px solid #00d4aa;
    margin-top:20px;
}
.answer h3 { color:#00d4aa !important; margin-top:0; }
.answer p { color:#e2e8f0 !important; font-size:1.05rem; line-height:1.6; }

/* Code block (architecture) */
.stCode, pre, code {
    background:#0d1f3c !important;
    color:#00d4aa !important;
}

/* Success message — green */
[data-testid="stAlert"] {
    background:rgba(0,212,170,0.1) !important;
    color:#e2e8f0 !important;
}

/* Dataframe */
.stDataFrame { color:#e2e8f0 !important; }

/* Subheaders */
h1, h2, h3, .stSubheader {
    color:#f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)


def render_stats():
    try:
        stats = get_stats()
    except Exception as e:
        st.warning(f"Stats unavailable: {e}")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", stats.get("total_companies", 0))
    c2.metric("Filings",   stats.get("total_filings", 0))
    c3.metric("Chunks",    f"{stats.get('total_chunks', 0):,}")
    c4.metric("Last updated", str(stats.get("last_updated", "—"))[:16])


def get_companies():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company FROM financial_metrics ORDER BY company;")
    rows = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_metrics(company=None):
    conn = get_connection()
    cur = conn.cursor()
    if company and company != "All":
        cur.execute(
            "SELECT company, fiscal_year, metric_name, metric_value "
            "FROM financial_metrics WHERE company = %s ORDER BY metric_name",
            (company,),
        )
    else:
        cur.execute(
            "SELECT company, fiscal_year, metric_name, metric_value "
            "FROM financial_metrics ORDER BY company, metric_name"
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


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
    options=["Ask AI", "System Stats", "Financials"],
    icons=["robot", "bar-chart", "cash-stack"],
    orientation="horizontal",
    styles={
        "container": {"background-color": "#0d1f3c", "border-radius": "10px"},
        "nav-link": {"color": "#94a3b8", "font-size": "15px"},
        "nav-link-selected": {"background-color": "#00d4aa", "color": "#020617"},
    }
)

if selected == "Ask AI":
    render_stats()
    question = st.text_input(
        "Ask a financial question",
        placeholder="Who is the CEO of Microsoft?"
    )
    if st.button("Analyze"):
        if question:
            st.session_state.history.append(question)
            with st.spinner("Analyzing financial documents..."):
                try:
                    retrieve_context(question)
                    answer = ask_question(question)
                except Exception as e:
                    answer = f"Error: {e}"
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
    st.code("""
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
Llama 3 / Groq
     ↓
Answer
""")
    st.success("Live data connected — pgvector + document_chunks")

if selected == "Financials":
    st.subheader("Extracted Financial Metrics")
    st.caption("AI-extracted from FY2025 10-K filings — experimental, verify before use.")
    try:
        company_list = ["All"] + get_companies()
        selected_company = st.selectbox("Select company", company_list)
        rows = get_metrics(selected_company)

        if rows:
            df = pd.DataFrame(rows, columns=["Company", "Fiscal Year", "Metric", "Value"])
            df["Metric"] = df["Metric"].str.replace("_", " ").str.title()
            st.dataframe(df, width='stretch', hide_index=True)
        else:
            st.info("No metrics found.")
    except Exception as e:
        st.warning(f"Metrics unavailable: {e}")