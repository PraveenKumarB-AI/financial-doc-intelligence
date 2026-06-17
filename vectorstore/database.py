import os
import psycopg2


def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "financial_rag"),
        user=os.getenv("DB_USER", "praveenkumarbotta"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    return conn