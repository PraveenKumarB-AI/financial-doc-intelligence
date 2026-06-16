from fastapi import FastAPI
from pydantic import BaseModel
from vectorstore.stats import get_stats
from rag.chain import ask_question
from rag.retriever import retrieve_context
from vectorstore.database import get_connection

app = FastAPI()


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Financial Document Intelligence API is running"
    }


@app.get("/stats")
def stats():
    return get_stats()


@app.post("/ask")
def ask(data: Question):
    context = retrieve_context(data.question)
    answer = ask_question(data.question)
    return {
        "answer": answer,
        "source": context[:2000]
    }

@app.get("/metrics")
def metrics(company: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if company:
        cur.execute(
            """
            SELECT company, fiscal_year, metric_name, metric_value
            FROM financial_metrics
            WHERE company = %s
            ORDER BY metric_name
            """,
            (company,),
        )
    else:
        cur.execute(
            """
            SELECT company, fiscal_year, metric_name, metric_value
            FROM financial_metrics
            ORDER BY company, metric_name
            """
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "metrics": [
            {"company": r[0], "fiscal_year": r[1], "metric": r[2], "value": r[3]}
            for r in rows
        ]
    }

@app.get("/companies")
def companies():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company FROM financial_metrics ORDER BY company;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"companies": [r[0] for r in rows]}