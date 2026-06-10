from fastapi import FastAPI
from pydantic import BaseModel

from rag.chain import ask_question

app = FastAPI(
    title="Financial RAG API"
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():

    return {
        "message": "Financial Document Intelligence API"
    }


@app.post("/ask")
def ask(data: Question):

    answer = ask_question(
        data.question
    )

    return {
        "question": data.question,
        "answer": answer
    }