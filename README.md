# Financial Document Intelligence Assistant

An AI-powered system that downloads, processes, and answers natural-language
questions about SEC financial filings using Retrieval-Augmented Generation
(RAG). It runs entirely on a free, local stack — no paid APIs, no paid cloud.

---

## Overview

The system ingests 10-K filings for multiple companies from SEC EDGAR, splits
them into chunks, embeds them into PostgreSQL + pgvector, retrieves the most
relevant chunks per question (automatically scoped to the right company), and
answers using a locally hosted Llama 3 model via Ollama. A FastAPI service and
Streamlit UI sit on top, with live stats, a financial metrics panel with a
company-filter dropdown, and a fully measured RAG evaluation harness.

---

## Tech Stack (100% free / open-source)

| Layer | Tool |
|---|---|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (384-dim) |
| Vector store | PostgreSQL 17 + pgvector |
| LLM | Llama 3 via Ollama (local, offline) |
| API | FastAPI + Uvicorn |
| UI | Streamlit |
| Data source | SEC EDGAR (public, free, no API key) |

---

## Project Status

The full RAG pipeline works end to end across three companies. 11,818 chunks
are stored in pgvector, each tagged with company name and fiscal year.
Questions are automatically routed to the right company's data. Structured
financial metrics are extracted per company using Llama 3 and stored in a
queryable table. A measured evaluation harness confirms 93% accuracy across
15 gold Q&A pairs.

---

## Companies & Extracted FY2025 Metrics

All figures extracted by Llama 3 from real SEC 10-K filings (FY2025).
Labeled experimental in the UI — verify against source filings before use.

| Company | Ticker | Chunks | Revenue (M) | Net Income (M) | EPS (Diluted) |
|---|---|---|---|---|---|
| Apple Inc. | AAPL | 3,101 | 400,869 | 112,010 | 7.46 |
| Microsoft Corporation | MSFT | 3,893 | 279,009 | 101,832 | 13.64 |
| Tesla, Inc. | TSLA | 4,824 | 97,690 | 3,794 | 1.08 |
| **Total** | | **11,818** | | | |

---

## Evaluation Results (Module 16)

Measured on 15 gold Q&A pairs across 3 companies (FY2025 10-K filings).
Run anytime with: `python -m evaluation.run_eval`

| Metric | Score |
|---|---|
| **Overall accuracy** | **14/15 (93%)** |
| **Avg latency** | **7.3s per question** |
| Apple Inc. | 5/5 (100%) |
| Microsoft Corporation | 5/5 (100%) |
| Tesla, Inc. | 4/5 (80%) |
| Financials category | 5/5 (100%) |
| Leadership category | 5/6 (83%) |
| Business category | 4/4 (100%) |

*Evaluated June 16, 2026. LLM judge: local Llama 3 via Ollama.*

---

## Roadmap & Progress

### Done

- **Module 1 — SEC Filing Downloader.** Downloads 10-K filings from SEC EDGAR
  for any ticker using the public submissions API. No API key, no cost.
- **Module 2 — Text Extraction.** Extracts clean text from HTML/TXT/PDF SEC
  filings using BeautifulSoup and PyMuPDF.
- **Module 3 — Chunking Engine.** Splits filings into overlapping 1,000-token
  chunks using LangChain RecursiveCharacterTextSplitter (200-token overlap).
- **Module 4 — Embedding Pipeline.** Generates 384-dim MiniLM embeddings
  locally via sentence-transformers. No external API calls.
- **Module 5 — Vector Database.** Stores chunks and embeddings in PostgreSQL
  with the pgvector extension. Cosine similarity search via `<=>` operator.
- **Module 6 — RAG Retrieval.** Semantic vector search with automatic company
  scoping — questions about Microsoft only search Microsoft chunks.
- **Module 7 — LLM Assistant.** Answers questions using local Llama 3 via
  Ollama. Fully offline, no paid API.
- **Module 8 — Pipeline Repair & Parsing.** Rebuilt the text extraction and
  chunking pipeline; fixed encoding issues in SEC filing text.
- **Module 9 — Metadata Ingestion.** Every chunk is tagged with company name,
  ticker (source), and fiscal year at ingest time. Enables company-scoped
  retrieval and per-company extraction.
- **Module 10–13 — Multi-company build-out.** Per-company ingestion script,
  company detector (maps question text to DB company name), FastAPI service,
  Streamlit UI with question history sidebar.
- **Module 14 — Live Corpus Stats.** `/stats` API endpoint and four live UI
  metric tiles (companies, filings, chunks, last updated) read directly from
  the database in real time.
- **Module 15 — Financial Extraction.** Local Llama 3 extracts structured
  financial metrics (revenue, net income, EPS) per company from
  company-scoped retrieved chunks. Results stored in `financial_metrics`
  table. `/metrics` and `/companies` endpoints expose the data. Streamlit
  Financials tab with company dropdown renders the table. Revenue validation
  guards against segment subtotals being mistaken for total revenue.
- **Module 16 — RAG Evaluation Harness.** 15-question gold Q&A set covering
  leadership, financials, and business questions for all three companies.
  Local Llama 3 acts as judge. Produces accuracy, per-company, per-category
  breakdown, and latency metrics. Results saved as timestamped JSON.
  **Result: 93% accuracy, 7.3s avg latency.**

### In progress / next

- **Module 17 — Logging & Monitoring.** Structured request/answer logging
  with timing and error tracking across the pipeline.
- **Module 18 — Testing Framework.** pytest suite covering ingestion,
  retrieval, and API endpoints.
- **Module 19 — Full Dockerization.** docker-compose standing up Postgres +
  pgvector, API, UI, and Ollama in one command.
- **Module 20 — Auth & Rate Limiting.** API key authentication and per-client
  rate limits on the FastAPI layer.
- **Module 21 — CI/CD + Free Cloud Deploy.** GitHub Actions CI on every push;
  deploy to Oracle Always-Free VM or Hugging Face Spaces (free Groq LLM
  endpoint for hosted version).
- **Module 22 — Capstone.** Architecture diagram, demo GIF, final README
  polish, portfolio write-up.

---

## Known Limitations

- `operating_income` and `gross_margin` extraction is inconsistent — the LLM
  finds revenue and net income reliably but sometimes misses these two from
  the filing's tabular layout. Tracked for a future extraction improvement.
- Tesla CFO (Vaibhav Taneja) was not found in retrieved chunks — his name
  appears in the certifications section which may not be retrieved by the
  income-statement-focused retrieval query. The one miss in the eval harness.
- Microsoft revenue extracted as 279,009M vs real 281,724M (~1% off).
  Tesla revenue 94,827M vs real 97,690M (~3% off). All figures are labeled
  experimental in the UI.
- Database credentials are hardcoded in `vectorstore/database.py` and will be
  moved to a `.env` file in Module 20.
- The `/ask` endpoint takes 6–45s because Llama 3 runs on CPU locally.
  Module 12 (streaming) and Module 21 (Groq free tier on cloud) will address
  response time for the hosted version.

---

## Project Structure

```
financial-doc-intelligence/
├── ingestion/
│   ├── sec_downloader.py       # download 10-K for any ticker
│   ├── ingest_company.py       # parse → chunk → tag → embed → load
│   ├── pdf_parser.py           # extract text from HTML/TXT/PDF
│   ├── chunker.py              # split text into overlapping chunks
│   └── metadata_builder.py    # detect company + fiscal year from text
├── embeddings/
│   └── embedding_generator.py  # MiniLM 384-dim local embeddings
├── vectorstore/
│   ├── schema.sql              # document_chunks + financial_metrics tables
│   ├── database.py             # psycopg2 connection helper
│   ├── search.py               # vector search with company filter
│   ├── stats.py                # live corpus statistics
│   ├── financial_extractor.py  # LLM-based per-company metric extraction
│   └── vector_loader.py        # legacy single-file loader (kept for ref)
├── rag/
│   ├── retriever.py            # detect company → scoped vector search
│   ├── chain.py                # prompt builder + Llama 3 call
│   └── text_cleaner.py         # strip HTML from retrieved chunks
├── llm/
│   └── llm_client.py           # Ollama Llama 3 wrapper
├── analytics/
│   └── company_detector.py     # map question text → DB company name
├── api/
│   └── app.py                  # FastAPI: / /stats /ask /metrics /companies
├── ui/
│   └── streamlit_app.py        # Streamlit: Ask AI, System Stats, Financials
├── evaluation/
│   ├── test_questions.json     # 15 gold Q&A pairs (3 companies × 5 Qs)
│   ├── run_eval.py             # evaluation harness + Llama 3 judge
│   └── results/                # timestamped JSON eval outputs
├── docker/                     # upcoming Module 19
├── config.py
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/PraveenKumarB-AI/financial-doc-intelligence.git
cd financial-doc-intelligence
python3 -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### Prerequisites

**PostgreSQL 17 + pgvector (Mac via Homebrew):**
```bash
brew install postgresql@17
brew services start postgresql@17
psql -U $(whoami) -d postgres -c "CREATE DATABASE financial_rag;"
psql -U $(whoami) -d financial_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Ollama + Llama 3:**
```bash
# Install from https://ollama.com/download
ollama pull llama3
```

---

## Usage

```bash
# 1. Create the database tables
psql -U $(whoami) -d financial_rag -f vectorstore/schema.sql

# 2. Download and ingest each company (repeat for MSFT, TSLA, etc.)
python -m ingestion.sec_downloader AAPL
python -m ingestion.ingest_company AAPL

python -m ingestion.sec_downloader MSFT
python -m ingestion.ingest_company MSFT

python -m ingestion.sec_downloader TSLA
python -m ingestion.ingest_company TSLA

# 3. Extract financial metrics for all companies
python -m vectorstore.financial_extractor

# 4. Run the evaluation harness
python -m evaluation.run_eval

# 5. Start the API (terminal 1)
uvicorn api.app:app --reload

# 6. Start the UI (terminal 2)
streamlit run ui/streamlit_app.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/stats` | GET | Live knowledge-base statistics |
| `/ask` | POST | Ask a question — body: `{"question": "..."}` |
| `/metrics` | GET | Extracted financial metrics (`?company=` filter optional) |
| `/companies` | GET | List of companies with extracted metrics |

---

## Example Questions

```
Who is the CEO of Microsoft?
What is Tesla's revenue for FY2025?
What are Apple's main risk factors?
Who is the CFO of Apple?
What is Microsoft's main cloud product?
What does Tesla manufacture?
```

---

## Data Source

SEC EDGAR — https://www.sec.gov/edgar (public domain, no API key required)

---

## Author

Praveen Kumar Botta — AI / ML Engineer
GitHub: https://github.com/PraveenKumarB-AI

---

## License

MIT License