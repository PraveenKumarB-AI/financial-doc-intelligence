# Financial Document Intelligence Assistant

An AI-powered system that downloads, processes, and answers natural-language
questions about SEC financial filings using Retrieval-Augmented Generation
(RAG). It runs entirely on a free, local stack — no paid APIs, no paid cloud.
Fully containerized with Docker, secured with API-key auth and rate limiting.

---

## Overview

The system ingests 10-K filings for multiple companies from SEC EDGAR, splits
them into chunks, embeds them into PostgreSQL + pgvector, retrieves the most
relevant chunks per question (automatically scoped to the right company), and
answers using a locally hosted Llama 3 model via Ollama. A FastAPI service and
Streamlit UI sit on top, with live stats, a financial metrics panel, a fully
measured RAG evaluation harness, structured JSON request logging, a 36-test
pytest suite, one-command Docker deployment, and API-key authentication with
per-client rate limiting.

---

## Tech Stack (100% free / open-source)

| Layer | Tool |
|---|---|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (384-dim) |
| Vector store | PostgreSQL 17 + pgvector |
| LLM | Llama 3 via Ollama (local, offline) |
| API | FastAPI + Uvicorn |
| UI | Streamlit |
| Logging | Python `logging` + structured JSON |
| Testing | pytest (36 tests) |
| Containerization | Docker + docker-compose |
| Security | API-key auth + slowapi rate limiting + python-dotenv |
| Data source | SEC EDGAR (public, free, no API key) |

---

## Project Status

The full RAG pipeline works end to end across three companies and runs in
Docker with a single command. Chunks are stored in pgvector, each tagged with
company name and fiscal year. Questions are automatically routed to the right
company's data. Structured financial metrics are extracted per company using
Llama 3. A measured evaluation harness confirms 93% accuracy across 15 gold
Q&A pairs. Every API request is logged to a structured JSON file, a 36-test
pytest suite covers the core logic, the whole stack is containerized, and the
expensive `/ask` endpoint is protected by API-key auth and rate limiting with
all secrets held in a `.env` file.

---

## Companies & Extracted FY2025 Metrics

All figures extracted by Llama 3 from real SEC 10-K filings (FY2025).
Labeled experimental in the UI — verify against source filings before use.

| Company | Ticker | Revenue (M) | Net Income (M) | EPS (Diluted) |
|---|---|---|---|---|
| Apple Inc. | AAPL | 400,869 | 112,010 | 7.46 |
| Microsoft Corporation | MSFT | 279,009 | 101,832 | 13.64 |
| Tesla, Inc. | TSLA | 97,690 | 3,794 | 1.08 |

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

## Security (Module 20)

The API uses API-key authentication and per-client rate limiting.

**API key** — the expensive `/ask` endpoint requires an `X-API-Key` header.
Missing or wrong key returns `401 Unauthorized`. Read endpoints (`/stats`,
`/companies`, `/metrics`) stay open so the data is viewable in a demo.

```bash
# Rejected — no key
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the CEO of Apple?"}'
# → {"detail":"Invalid or missing API key"}

# Accepted — with key
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-key>" \
  -d '{"question": "Who is the CEO of Apple?"}'
```

**Rate limiting** — `/ask` is limited to 20 requests/minute per IP via
`slowapi`. Exceeding it returns `429 Too Many Requests`.

**Secrets** — database credentials and the API key live in a `.env` file
(git-ignored), loaded via `python-dotenv`. `database.py` and `app.py` read
from the environment, so the same code runs locally and in Docker.

```
# .env (not committed)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_rag
DB_USER=praveenkumarbotta
DB_PASSWORD=
API_KEY=your-secret-key
```

---

## Logging & Monitoring (Module 17)

Every API request writes a structured JSON line to `logs/api.log`:

```json
{"ts":"2026-06-16T23:23:25+00:00","endpoint":"/ask","status":"ok","latency_s":8.341,"question":"Who is the CEO of Microsoft?","company":"Microsoft Corporation","answer":"Satya Nadella..."}
```

Fields logged per request: timestamp (UTC), endpoint, status (ok/error),
latency in seconds, question text, detected company, answer snippet, and
error message on failure.

View live logs via the API:
```bash
curl "http://127.0.0.1:8000/logs?n=20"
```

---

## Testing (Module 18)

A 36-test pytest suite runs in ~6 seconds with no LLM calls (deliberately
fast — answer quality is measured separately in the evaluation harness).

```bash
python -m pytest tests/ -v
```

```
36 passed in 6.22s
```

| Test file | Coverage |
|---|---|
| `test_api.py` | All 6 endpoints — status codes, response shapes, company filter |
| `test_company_detector.py` | Company detection from question text |
| `test_logger.py` | Log writing and reading, error status |
| `test_chunker.py` | Text chunking output and size limits |
| `test_search.py` | Vector search, company filtering, isolation |

---

## Docker Deployment (Module 19)

The entire stack runs in three containers with one command:

```bash
docker compose up -d --build
```

| Container | Service | Port |
|---|---|---|
| `findoc_db` | PostgreSQL 17 + pgvector | 5432 |
| `findoc_api` | FastAPI | 8000 |
| `findoc_ui` | Streamlit | 8501 |

The database schema is auto-created from `vectorstore/schema.sql` on first
startup. The API container reaches Ollama running on the host machine via
`host.docker.internal:11434`, so the LLM stays on the host (no GPU passthrough
needed) while everything else is containerized.

**Notes:**
- The Dockerfile installs CPU-only PyTorch (`--index-url https://download.pytorch.org/whl/cpu`) to avoid pulling ~2GB of unused CUDA GPU libraries.
- `database.py` and `app.py` read settings from environment variables, so the
  same code works in Docker and on the host.
- Ollama must be running on the host before asking questions.

**Load data into the containers:**
```bash
docker compose exec api python -m ingestion.sec_downloader AAPL
docker compose exec api python -m ingestion.ingest_company AAPL
# repeat for MSFT, TSLA
docker compose exec api python -m vectorstore.financial_extractor
```

**Stop everything:**
```bash
docker compose down
```

When using Docker, do not run a local `uvicorn` or `streamlit` at the same
time — the containers own ports 8000 and 8501.

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
- **Module 17 — Logging & Monitoring.** Structured JSON logger writes one
  line per API request to `logs/api.log` covering timestamp, endpoint,
  latency, detected company, answer snippet, and ok/error status. The
  `/logs?n=N` endpoint returns the last N entries as JSON for live
  monitoring. Error handling in `/ask` catches exceptions and logs them with
  status `"error"` instead of crashing silently.
- **Module 18 — Testing Framework.** 36-test pytest suite covering all six
  API endpoints, company detection, logging, chunking, and vector search.
  Runs in ~6 seconds with no LLM calls. `pytest.ini` silences third-party
  deprecation warnings for clean output.
- **Module 19 — Dockerization.** Three-container docker-compose stack
  (Postgres + pgvector, FastAPI, Streamlit) starting with one command. Schema
  auto-loaded on startup. CPU-only PyTorch keeps the image lean. The API
  reaches host Ollama via `host.docker.internal`. Connection settings read
  from environment variables so the same code runs in Docker and locally.
- **Module 20 — Auth & Rate Limiting.** The `/ask` endpoint requires an
  `X-API-Key` header (401 if missing/wrong) and is rate-limited to 20
  requests/minute per IP via `slowapi` (429 if exceeded). Database
  credentials and the API key moved to a git-ignored `.env` file loaded with
  `python-dotenv`. The Streamlit UI sends the key automatically so the Ask AI
  tab keeps working.

### In progress / next

- **Module 21 — CI/CD + Free Cloud Deploy.** GitHub Actions CI running the
  36-test suite on every push; deploy to Oracle Always-Free VM or Hugging
  Face Spaces (free Groq LLM endpoint for the hosted version); status badges.
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
  Tesla revenue extracted as 97,690M (~3% off actual). All figures are
  labeled experimental in the UI.
- The `/ask` endpoint takes 6–45s because Llama 3 runs on CPU. Module 21
  (Groq free tier on cloud) will address response time for the hosted version.
- The default API key in the repo is a demo placeholder — set a strong value
  in `.env` for any real deployment.

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
│   ├── database.py             # psycopg2 connection (env-var driven)
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
│   └── app.py                  # FastAPI + API-key auth + rate limiting
├── ui/
│   └── streamlit_app.py        # Streamlit: Ask AI, System Stats, Financials
├── evaluation/
│   ├── test_questions.json     # 15 gold Q&A pairs (3 companies × 5 Qs)
│   ├── run_eval.py             # evaluation harness + Llama 3 judge
│   └── results/                # timestamped JSON eval outputs
├── logs/
│   ├── logger.py               # structured JSON request logger
│   ├── __init__.py
│   └── api.log                 # live request log (auto-created)
├── tests/
│   ├── test_api.py             # endpoint tests (15)
│   ├── test_company_detector.py# detection tests (6)
│   ├── test_logger.py          # logging tests (5)
│   ├── test_chunker.py         # chunking tests (5)
│   ├── test_search.py          # search tests (5)
│   └── __init__.py
├── Dockerfile                  # CPU-only Python app image
├── docker-compose.yml          # db + api + ui services
├── .dockerignore
├── .env                        # secrets (git-ignored)
├── .gitignore
├── pytest.ini
├── config.py
├── requirements.txt
└── README.md
```

---

## Installation (local, without Docker)

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

**Create your `.env`:**
```bash
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_rag
DB_USER=your_pg_user
DB_PASSWORD=
API_KEY=your-secret-key
EOF
```

---

## Usage (local)

```bash
# 1. Create the database tables
psql -U $(whoami) -d financial_rag -f vectorstore/schema.sql

# 2. Download and ingest each company
python -m ingestion.sec_downloader AAPL
python -m ingestion.ingest_company AAPL
# repeat for MSFT, TSLA

# 3. Extract financial metrics for all companies
python -m vectorstore.financial_extractor

# 4. Run the evaluation harness
python -m evaluation.run_eval

# 5. Run the test suite
python -m pytest tests/ -v

# 6. Start the API (terminal 1)
uvicorn api.app:app --reload

# 7. Start the UI (terminal 2)
streamlit run ui/streamlit_app.py
```

For the Docker workflow, see the **Docker Deployment** section above.

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | — | Health check |
| `/stats` | GET | — | Live knowledge-base statistics |
| `/ask` | POST | API key + rate limit | Ask a question — body: `{"question": "..."}` |
| `/metrics` | GET | — | Extracted financial metrics (`?company=` filter optional) |
| `/companies` | GET | — | List of companies with extracted metrics |
| `/logs` | GET | — | Last N request log entries (`?n=50` default) |

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