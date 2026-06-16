"""
vectorstore/financial_extractor.py — MODULE 15: Multi-company Financial Extraction
Extracts key financial metrics for each company using local Llama 3.
Run:  python -m vectorstore.financial_extractor
"""

import json
from embeddings.embedding_generator import generate_embedding
from vectorstore.database import get_connection
from llm.llm_client import generate_response

COMPANIES = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "fiscal_year": "2025",
        "revenue_hint": "approximately 400,869 million",
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "fiscal_year": "2025",
        "revenue_hint": "approximately 279,009 million",
    },
    {
        "ticker": "TSLA",
        "name": "Tesla, Inc.",
        "fiscal_year": "2025",
        "revenue_hint": "approximately 97,690 million",
    },
]

RETRIEVAL_QUERY = (
    "CONSOLIDATED STATEMENTS OF OPERATIONS total net sales twelve months "
    "annual revenue net income operating income earnings per share full year"
)


def get_financial_chunks(ticker, top_k=15):
    """Retrieve chunks belonging to this company only."""
    embedding = str(generate_embedding(RETRIEVAL_QUERY))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT chunk_text
        FROM document_chunks
        WHERE source = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (ticker, embedding, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]


def extract_metrics(company_name, fiscal_year, revenue_hint, context):
    """Ask Llama 3 to extract key figures as strict JSON."""
    prompt = f"""
You are a financial data extractor reading a {company_name} 10-K annual filing
for fiscal year {fiscal_year}.

CRITICAL RULES:
- Use ONLY full-year annual figures (12 months ended), NOT quarterly figures.
- total_revenue is the SINGLE largest revenue/net sales line for the full year.
  For {company_name} FY{fiscal_year} this should be {revenue_hint}.
- Do NOT use segment subtotals or quarterly numbers.

Extract these metrics:
- total_revenue
- net_income
- operating_income
- earnings_per_share_diluted
- gross_margin

Return ONLY valid JSON, no explanation, exactly this format:
{{"total_revenue": "", "net_income": "", "operating_income": "", "earnings_per_share_diluted": "", "gross_margin": ""}}

Use empty string if not found. Values in millions unless EPS.

Context:
{context}
"""
    raw = generate_response(prompt)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        print("   Model returned prose — using empties.")
        return {
            "total_revenue": "", "net_income": "", "operating_income": "",
            "earnings_per_share_diluted": "", "gross_margin": ""
        }
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        print("   JSON parse error — using empties.")
        return {
            "total_revenue": "", "net_income": "", "operating_income": "",
            "earnings_per_share_diluted": "", "gross_margin": ""
        }


def _to_number(value):
    digits = "".join(c for c in str(value) if c.isdigit() or c == ".")
    try:
        return float(digits)
    except ValueError:
        return 0.0


def validate(metrics):
    rev = _to_number(metrics.get("total_revenue", ""))
    others = [
        _to_number(v) for k, v in metrics.items()
        if k != "total_revenue"
    ]
    if rev and others and rev < max(others):
        print(f"   WARNING: revenue ({rev}) < another metric ({max(others)}) — blanking.")
        metrics["total_revenue"] = ""
    return metrics


def store_metrics(company, fiscal_year, metrics):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM financial_metrics WHERE company = %s AND fiscal_year = %s",
        (company, fiscal_year),
    )
    inserted = 0
    for name, value in metrics.items():
        if value and str(value).strip():
            cur.execute(
                """
                INSERT INTO financial_metrics
                    (company, fiscal_year, metric_name, metric_value, unit)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (company, fiscal_year, name, str(value), ""),
            )
            inserted += 1
    conn.commit()
    cur.close()
    conn.close()
    return inserted


def run():
    for c in COMPANIES:
        print(f"\n{'='*50}")
        print(f"  {c['name']} ({c['fiscal_year']})")
        print(f"{'='*50}")
        try:
            print("1. Retrieving chunks...")
            chunks = get_financial_chunks(c["ticker"])
            if not chunks:
                print("   No chunks found — skipping.")
                continue
            context = "\n\n".join(chunks)

            print("2. Extracting metrics...")
            metrics = extract_metrics(
                c["name"], c["fiscal_year"], c["revenue_hint"], context
            )
            metrics = validate(metrics)
            print(f"   {metrics}")

            print("3. Storing...")
            n = store_metrics(c["name"], c["fiscal_year"], metrics)
            print(f"   Stored {n} metric(s).")

        except Exception as e:
            print(f"   ERROR for {c['name']}: {e}")
            continue


if __name__ == "__main__":
    run()