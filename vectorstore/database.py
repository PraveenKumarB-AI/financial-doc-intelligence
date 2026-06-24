import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def _get_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    return None


def get_connection():
    database_url = _get_database_url()
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "financial_rag"),
        user=os.getenv("DB_USER", "praveenkumarbotta"),
        password=os.getenv("DB_PASSWORD", ""),
    )
