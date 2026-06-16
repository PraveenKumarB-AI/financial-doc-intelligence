from fastapi import FastAPI
from pydantic import BaseModel
from vectorstore.stats import get_stats
from rag.chain import ask_question
from rag.retriever import retrieve_context

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