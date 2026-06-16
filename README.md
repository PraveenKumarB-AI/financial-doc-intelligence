# Financial Document Intelligence Assistant

An AI-powered system that downloads, processes, and answers natural-language
questions about SEC financial filings using Retrieval-Augmented Generation
(RAG). It runs entirely on a free, local stack — no paid APIs.

## Overview

The system ingests 10-K filings for multiple companies from SEC EDGAR, splits
them into chunks, embeds them into a PostgreSQL + pgvector database, retrieves
the most relevant chunks per question (scoped to the right company
automatically), and answers using a locally hosted Llama 3 model. A FastAPI
service and Streamlit UI sit on top, with live stats, a financial metrics
panel, and a company-filter dropdown.

## Tech Stack (100% free / open-source)

- **Embeddings:** sentence-transformers `all-MiniLM-L6-v2` (384-dim)
- **Vector store:** PostgreSQL + pgvector
- **LLM:** Llama 3 served locally via Ollama
- **API:** FastAPI + Uvicorn
- **UI:** Streamlit
- **Data source:** SEC EDGAR (public, free, no API key)

## Project Status

The full RAG pipeline works end to end across three companies. 11,818 chunks
are stored in pgvector, each tagged with company name and fiscal year.
Questions are automatically routed to the right company's data. Structured
financial metrics are extracted per company using Llama 3 and stored in a
queryable table. A FastAPI service exposes the system and a Streamlit UI
provides chat, live stats, and a financial metrics panel with a company
dropdown.

## Companies & Extracted FY2025 Metrics

All figures extracted by Llama 3 from real SEC 10-K filings (FY2025).
Labeled experimental — verify against source filings before relying on them.

| Company | Chunks | Revenue (M) | Net Income (M) | EPS (Diluted) |
|---|---|---|---|---|
| Apple Inc. | 3,101 | 400,869 | 112,010 | 7.46 |
| Microsoft Corporation | 3,893 | 279,009 | 101,832 | 13.64 |
| Tesla, Inc. | 4,824 | 97,690 | 3,794 | 1.08 |
| **Total** | **11,818** | | | |

## Roadmap & Progress

### Done

- **Module 1 — SEC Filing Downloader.** Pulls 10-K filings from SEC EDGAR
  for any ticker using the public submissions API. No API key required.
- **Module 2 — Text Extraction.** Extracts clean text from HTML/TXT SEC
  filings using BeautifulSoup and PyMuPDF.
- **Module 3 — Chunking Engine.** Splits filings into overlapping 1,000-token
  chunks using LangChain's RecursiveCharacterTextSplitter.
- **Module 4 — Embedding Pipeline.** Generates 384-dim MiniLM embeddings
  locally via sentence-transformers.
- **Module 5 — Vector Database.** Stores chunks and embeddings in PostgreSQL
  with the pgvector extension for semantic similarity search.
- **Module 6 — RAG Retrieval.** Semantic search with optional company filter
  so questions are automatically scoped to the right company's data.
- **Module 7 — LLM Assistant.** Answers questions using local Llama 3 via
  Ollama — fully offline, no paid API.
- **Module 8–13 — Pipeline build-out.** Multi-company ingestion script,
  metadata-aware chunking (company + fiscal year tagged per chunk), FastAPI
  service, Streamlit UI, company detection from natural-language questions.
- **Module 14 — Live Corpus Stats.** `/stats` endpoint and four live UI tiles
  (companies, filings, chunks, last updated) read directly from the database.
- **Module 15 — Financial Extraction.** Llama 3 extracts structured financial
  metrics (revenue, net income, EPS) per company from retrieved chunks and
  stores them in a `financial_metrics` table. `/metrics` and `/companies`
  endpoints expose the data. Streamlit Financials tab with company dropdown
  displays the results. Extraction validated per company against real filings.

### In progress / next

- **Module 16 — RAG Evaluation Harness.** Gold Q&A set + accuracy/latency
  metrics table measured with local Llama 3 as judge.
- **Module 17 — Logging & Monitoring.**
- **Module 18 — Testing Framework (pytest).**
- **Module 19 — Full Dockerization (docker-compose).**
- **Module 20 — Auth & Rate Limiting.**
- **Module 21 — CI/CD + Free Cloud Deploy.**
- **Module 22 — Capstone polish (diagram, demo GIF, metrics table, badges).**

## Known Limitations

- `operating_income` and `gross_margin` extraction is inconsistent — the LLM
  locates revenue and net income reliably but sometimes misses these two from
  the filing's tabular layout. Tracked for Module 16 evaluation.
- Microsoft revenue extracted as 279,009M vs real 281,700M (~1% off). Tesla
  net income is approximate. All figures labeled experimental in the UI.
- Database credentials are hardcoded in `vectorstore/database.py` and will be
  moved to a `.env` file in Module 20.
- The `/ask` endpoint is slow (~15–45s) because Llama 3 runs on CPU locally.
  Module 12 (streaming) and Module 21 (cloud deploy with Groq free tier) will
  address this.

## Project Structure

```
financial-doc-intelligence/
├── ingestion/
│   ├── sec_downloader.py      # download 10-K for any ticker
│   ├── ingest_company.py      # parse → chunk → tag → load one company
│   ├── pdf_parser.py          # extract text from HTML/TXT/PDF
│   ├── chunker.py             # split text into overlapping chunks
│   └── metadata_builder.py   # extract company + fiscal year from text
├── embeddings/
│   └── embedding_generator.py # MiniLM 384-dim embeddings
├── vectorstore/
│   ├── schema.sql             # document_chunks + financial_metrics tables
│   ├── database.py            # psycopg2 connection helper
│   ├── vector_loader.py       # legacy single-file loader
│   ├── search.py              # vector search with optional company filter
│   ├── stats.py               # live corpus statistics
│   └── financial_extractor.py # LLM-based per-company metric extraction
├── rag/
│   ├── retriever.py           # detect company → scoped vector search
│   ├── chain.py               # prompt builder + LLM call
│   └── text_cleaner.py        # strip HTML tags from chunks
├── llm/
│   └── llm_client.py          # Ollama Llama 3 wrapper
├── analytics/
│   └── company_detector.py    # detect company name from question text
├── api/
│   └── app.py                 # FastAPI: /, /stats, /ask, /metrics, /companies
├── ui/
│   └── streamlit_app.py       # Streamlit: Ask AI, System Stats, Financials
├── evaluation/                # upcoming Module 16
├── docker/                    # upcoming Module 19
├── config.py
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/PraveenKumarB-AI/financial-doc-intelligence.git
cd financial-doc-intelligence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Prerequisites

PostgreSQL 17 with pgvector:
```bash
brew install postgresql@17
brew services start postgresql@17
psql -U $(whoami) -d postgres -c "CREATE DATABASE financial_rag;"
psql -U $(whoami) -d financial_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Ollama with Llama 3:
```bash
# Install from https://ollama.com/download
ollama pull llama3
```

## Usage

```bash
# 1. Create the tables
psql -U $(whoami) -d financial_rag -f vectorstore/schema.sql

# 2. Download and ingest a company (run for each ticker)
python -m ingestion.sec_downloader AAPL
python -m ingestion.ingest_company AAPL

python -m ingestion.sec_downloader MSFT
python -m ingestion.ingest_company MSFT

python -m ingestion.sec_downloader TSLA
python -m ingestion.ingest_company TSLA

# 3. Extract financial metrics for all companies
python -m vectorstore.financial_extractor

# 4. Start the API (terminal 1)
uvicorn api.app:app --reload

# 5. Start the UI (terminal 2)
streamlit run ui/streamlit_app.py
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/stats` | GET | Live knowledge-base statistics |
| `/ask` | POST | Ask a question — body: `{"question": "..."}` |
| `/metrics` | GET | Extracted financial metrics (optional `?company=` filter) |
| `/companies` | GET | List of companies with extracted metrics |

## Example Questions

```
Who is the CEO of Microsoft?
What is Tesla's revenue for FY2025?
What are Apple's main risk factors?
What are the main risks facing technology companies?
```

## Data Source

SEC EDGAR Database — https://www.sec.gov/edgar

## Author

Praveen Kumar Botta — AI / ML Engineer

## License

MIT License