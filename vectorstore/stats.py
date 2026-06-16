"""
vectorstore/stats.py — MODULE 14: live corpus statistics
Reads counts from the document_chunks table using the project's real DB
connection. Test alone with:  python -m vectorstore.stats
"""

from vectorstore.database import get_connection

TABLE = "document_chunks"


def _scalar(cur, sql):
    """Run a query that returns one value; return None instead of crashing
    if a column or table doesn't exist."""
    try:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else None
    except Exception:
        return None


def get_stats():
    conn = get_connection()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            chunks    = _scalar(cur, f"SELECT COUNT(*) FROM {TABLE};")
            companies = _scalar(cur, f"SELECT COUNT(DISTINCT company) FROM {TABLE} WHERE company IS NOT NULL;")
            sources   = _scalar(cur, f"SELECT COUNT(DISTINCT source) FROM {TABLE} WHERE source IS NOT NULL;")
            updated   = _scalar(cur, f"SELECT MAX(created_at) FROM {TABLE};")
    finally:
        conn.close()
    return {
        "total_companies": companies or 0,
        "total_filings":   sources or 0,
        "total_chunks":    chunks or 0,
        "last_updated":    str(updated) if updated else "—",
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(get_stats())