"""
ingestion/ingest_company.py — Multi-company ingestion
For one ticker: find its latest 10-K, parse → chunk → tag with company +
fiscal_year + source, and load into document_chunks.
Run:  python -m ingestion.ingest_company AAPL
"""

import re
import sys
import glob

from ingestion.pdf_parser import extract_text
from ingestion.chunker import chunk_text
from embeddings.embedding_generator import generate_embedding
from vectorstore.database import get_connection

# Friendly company names per ticker
COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "TSLA": "Tesla, Inc.",
    "JPM":  "JPMorgan Chase & Co.",
    "AMZN": "Amazon.com, Inc.",
}


def find_latest_filing(ticker):
    """Return the path to the most recent 10-K full-submission.txt for a ticker."""
    pattern = f"data/raw/sec-edgar-filings/{ticker}/10-K/*/full-submission.txt"
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No 10-K found for {ticker} at {pattern}")
    return matches[-1]   # last = most recent accession


def detect_fiscal_year(text):
    """Pull the fiscal year from the filing text. Falls back to 'Unknown'."""
    m = re.search(r"fiscal year ended\s+[A-Za-z]+\s+\d+,\s+(\d{4})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"For the fiscal year ended.*?(\d{4})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return "Unknown"


def ingest(ticker):
    ticker = ticker.upper()
    company = COMPANY_NAMES.get(ticker, ticker)

    print(f"1. Locating {ticker} filing...")
    path = find_latest_filing(ticker)
    print(f"   {path}")

    print("2. Extracting text...")
    text = extract_text(path)

    fiscal_year = detect_fiscal_year(text)
    print(f"   Company={company}  FiscalYear={fiscal_year}")

    print("3. Chunking...")
    chunks = chunk_text(text)
    print(f"   {len(chunks)} chunks")

    print("4. Embedding + loading (this takes a bit)...")
    conn = get_connection()
    cur = conn.cursor()
    # Remove any prior chunks for this company so re-running doesn't duplicate
    cur.execute("DELETE FROM document_chunks WHERE company = %s", (company,))
    for chunk in chunks:
        embedding = str(generate_embedding(chunk))
        cur.execute(
            """
            INSERT INTO document_chunks
                (chunk_text, metadata, embedding, company, source, fiscal_year)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (chunk, "{}", embedding, company, ticker, fiscal_year),
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Done. Loaded {len(chunks)} chunks for {company} ({fiscal_year}).")


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    ingest(ticker)
