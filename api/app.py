import os
import time
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from vectorstore.stats import get_stats
from rag.chain import ask_question
from rag.retriever import retrieve_context
from vectorstore.database import get_connection
from logs.logger import log_request, read_logs

load_dotenv()

API_KEY = os.getenv("API_KEY", "findoc-demo-key-2026")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Financial Document Intelligence API",
    description="RAG over SEC 10-K filings — AAPL, MSFT, TSLA",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


def verify_api_key(x_api_key: str = Header(None)):
    """Require a valid X-API-Key header. Raises 401 if missing or wrong."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/")
def home():
    log_request(endpoint="/", status="ok", latency_s=0)
    return {"message": "Financial Document Intelligence API is running"}


@app.get("/stats")
def stats_route():
    t0 = time.time()
    result = get_stats()
    log_request(endpoint="/stats", status="ok", latency_s=time.time() - t0)
    return result


@app.post("/ask")
@limiter.limit("20/minute")
def ask(data: Question, request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    t0 = time.time()
    try:
        context = retrieve_context(data.question)
        answer  = ask_question(data.question)
        latency = time.time() - t0

        detected = None
        for name in ["Apple Inc.", "Microsoft Corporation", "Tesla, Inc."]:
            if name.split()[0].lower() in data.question.lower():
                detected = name
                break

        log_request(
            endpoint="/ask",
            question=data.question,
            company=detected,
            answer=answer,
            latency_s=latency,
            status="ok",
        )
        return {"answer": answer, "source": context[:2000]}

    except HTTPException:
        raise
    except Exception as e:
        log_request(
            endpoint="/ask",
            question=data.question,
            latency_s=time.time() - t0,
            status="error",
            error=str(e),
        )
        return {"answer": f"Error: {e}", "source": ""}


@app.get("/metrics")
def metrics(company: str = None):
    t0 = time.time()
    conn = get_connection()
    cur  = conn.cursor()
    if company:
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
    log_request(endpoint="/metrics", company=company, status="ok",
                latency_s=time.time() - t0)
    return {
        "metrics": [
            {"company": r[0], "fiscal_year": r[1], "metric": r[2], "value": r[3]}
            for r in rows
        ]
    }


@app.get("/companies")
def companies():
    t0 = time.time()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT company FROM financial_metrics ORDER BY company;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    log_request(endpoint="/companies", status="ok", latency_s=time.time() - t0)
    return {"companies": [r[0] for r in rows]}


@app.get("/logs")
def logs_route(n: int = 50):
    """Return the last n log entries as JSON."""
    return {"logs": read_logs(n)}