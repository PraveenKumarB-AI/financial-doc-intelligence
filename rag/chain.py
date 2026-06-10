from ollama import chat

from rag.retriever import retrieve_context
from rag.prompts import RAG_PROMPT


def ask_question(question):

    context = retrieve_context(question)

    prompt = RAG_PROMPT.format(
        context=context,
        question=question
    )

    response = chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]