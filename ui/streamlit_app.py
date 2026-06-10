import streamlit as st
import requests
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Financial AI Platform",
    page_icon="📈",
    layout="wide"
)

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

st.markdown("""
<div class="hero">
<h1>📈 Financial AI Platform</h1>
<p>SEC Filing Analysis using RAG + Llama 3 + pgvector</p>
</div>
""", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=[
        "Ask AI",
        "System Stats"
    ],
    icons=[
        "robot",
        "bar-chart"
    ],
    orientation="horizontal"
)

if selected == "Ask AI":

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric(
            "Documents",
            "12,289"
        )

    with col2:
        st.metric(
            "Model",
            "Llama 3"
        )

    with col3:
        st.metric(
            "Database",
            "pgvector"
        )

    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True
    )

    question = st.text_input(
        "Ask a financial question",
        placeholder="Who is the CEO?"
    )

    if st.button(
        "Analyze"
    ):

        with st.spinner(
            "Analyzing financial documents..."
        ):

            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={
                    "question": question
                }
            )

            answer = response.json()[
                "answer"
            ]

            st.markdown(
                f"""
                <div class="answer">
                <h3>Answer</h3>
                <p>{answer}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

if selected == "System Stats":

    st.subheader(
        "RAG Architecture"
    )

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

    st.success(
        "Modules 1-5 Completed"
    )