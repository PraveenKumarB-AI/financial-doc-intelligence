"""
llm/llm_client.py — LLM assistant with dual backend.
Uses Groq (hosted Llama 3) when GROQ_API_KEY is set (for cloud deployment),
otherwise falls back to local Ollama (for local development).
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq's current Llama 3 model name
GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_MODEL = "llama3"


def generate_response(prompt):
    """Send the prompt to Groq (if key set) or local Ollama, return the text."""
    if GROQ_API_KEY:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()
    else:
        import ollama
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()