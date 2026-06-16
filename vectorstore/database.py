import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="financial_rag",
        user="praveenkumarbotta",
        password=""          # Homebrew local users typically need no password
    )
    return conn
