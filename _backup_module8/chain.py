from llm.llm_client import (
    generate_response
)

from rag.retriever import (
    retrieve_context
)


def ask_question(question):

    context = retrieve_context(
        question
    )

    prompt = f"""
You are a financial analyst assistant.

Answer using ONLY the provided context.

Rules:
- Give short and direct answers.
- Do not say "According to the provided context".
- Do not mention HTML tags.
- Do not copy raw formatting.
- If the answer is not found, say:
  "I could not find that information in the filing."

Context:
{context}

Question:
{question}

Answer:
"""

    answer = generate_response(
        prompt
    )

    return answer