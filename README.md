# Financial Document Intelligence Assistant

An AI-powered system that downloads, processes, and answers natural-language
questions about SEC financial filings using Retrieval-Augmented Generation
(RAG). It runs entirely on a free, local stack — no paid APIs.

## Overview

The system ingests SEC filings, splits them into chunks, embeds them into a
PostgreSQL + pgvector database, retrieves the most relevant chunks for a
question, and answers using a locally hosted Llama 3 model. A Streamlit UI and
a FastAPI service sit on top, with a live stats panel showing the current state
of the knowledge base.

## Tech Stack (100% free / open-source)

- **Embeddings:** sentence-transformers `all-MiniLM-L6-v2` (384-dim)
- **Vector store:** PostgreSQL + pgvector
- **LLM:** Llama 3 served locally via Ollama
- **API:** FastAPI + Uvicorn
- **UI:** Streamlit
- **Data source:** SEC EDGAR (public, free)

## Project Status

The core RAG pipeline works end to end: real SEC filings are ingested,
embedded, stored in pgvector (3,660 chunks loaded), retrieved by semantic
similarity, and answered by Llama 3. A FastAPI layer exposes the system and a
Streamlit UI provides chat plus a live statistics panel.

## Roadmap & Progress

### Done

- **Module 1 — SEC Filing Downloader.** Pulls filings from SEC EDGAR.
- **Module 2 — Text Extraction.** Extracts text from downloaded filings.
- **Module 3 — Chunking Engine.** Splits filings into overlapping chunks.
- **Module 4 — Embedding Pipeline.** Generates 384-dim MiniLM embeddings.
- **Module 5 — Vector Database.** Stores chunks + embeddings in pgvector.
- **Module 6 — RAG Retrieval.** Semantic search over stored chunks.
- **Module 7 — LLM Assistant.** Answers questions with local Llama 3 via Ollama.
- **Module 8–13 — Pipeline build-out.** Ingestion, API, and UI scaffolding.
- **Module 14 — Live Corpus Stats.** `/stats` endpoint and UI tiles showing
  live counts (chunks, last updated) read directly from the database.

### In progress / next

- **Module 15 — Financial Extraction.** Pull structured figures (revenue, EPS,
  ratios) into queryable fields.
- **Module 16 — RAG Evaluation Harness.** Gold Q&A set + accuracy/latency metrics.
- **Module 17 — Logging & Monitoring.**
- **Module 18 — Testing Framework (pytest).**
- **Module 19 — Full Dockerization (docker-compose).**
- **Module 20 — Auth & Rate Limiting.**
- **Module 21 — CI/CD + Free Cloud Deploy.**
- **Module 22 — Capstone polish (diagram, demo, docs).**

## Known Limitations

These are tracked and slated for upcoming modules:

- Chunk metadata is currently stored empty, so the "Companies" and "Filings"
  stats read 0 (fixed in the metadata-aware ingestion work).
- The loader appends on every run rather than replacing, which can create
  duplicate rows if run multiple times.
- Database credentials are currently in code and will be moved to a `.env`
  file (Module 20).

## Project Structure

```
financial-doc-intelligence/
├── ingestion/        # SEC download + text extraction
├── embeddings/       # MiniLM embedding generation
├── vectorstore/      # pgvector schema, loader, search, stats, DB connection
├── rag/              # retriever + RAG chain
├── llm/              # local Llama 3 (Ollama) client
├── api/              # FastAPI service (/, /stats, /ask)
├── ui/               # Streamlit app
├── evaluation/       # evaluation scripts (upcoming)
├── docker/           # containerization (upcoming)
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

- PostgreSQL with the `pgvector` extension
- Ollama with Llama 3 pulled:
  ```bash
  ollama pull llama3
  ```

## Usage

```bash
# 1. Create the table
psql -d financial_rag -f vectorstore/schema.sql

# 2. Load chunks into the vector store
python -m vectorstore.vector_loader

# 3. Start the API
uvicorn api.app:app --reload

# 4. Start the UI (in a second terminal)
streamlit run ui/streamlit_app.py
```

API endpoints:

- `GET /` — health check
- `GET /stats` — live knowledge-base statistics
- `POST /ask` — ask a question about the filings

## Data Source

SEC EDGAR Database — https://www.sec.gov/edgar

## Author

Praveen Kumar Botta — AI / ML Engineer

## License

MIT License