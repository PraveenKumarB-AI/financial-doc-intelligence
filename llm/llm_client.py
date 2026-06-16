"""
llm/llm_client.py — Module 7: the LLM assistant
Sends a prompt to the local Llama 3 model (via Ollama) and returns the text.
This is what makes /ask actually answer questions.
"""

import ollama

MODEL = "llama3"   # matches `ollama list` on this machine


def generate_response(prompt):
    """Send the prompt to local Llama 3 and return the answer as a string."""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
