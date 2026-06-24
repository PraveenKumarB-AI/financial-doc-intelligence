# Financial Document Intelligence Assistant

![CI](https://github.com/PraveenKumarB-AI/financial-doc-intelligence/actions/workflows/ci.yml/badge.svg)

*Live demo:https://financial-doc-intelligence-gbnxwwhxj7d3fyqw4if6pn.streamlit.app

An AI assistant that reads SEC 10-K filings and answers plain-English questions about them. Ask it who runs a company, what its revenue was, or what risks it flagged, and it pulls the answer straight from the actual filing text using retrieval-augmented generation.

It runs two ways. Locally, everything is free and offline: a local Llama 3 model through Ollama, and PostgreSQL with pgvector for the search. The live version swaps in two free hosted services so it can run on the cloud without a beefy server: Groq for the language model and Neon for the database.

## What it does

You ask a question in the chat. The system finds the most relevant passages from the right company's filing, hands them to the language model along with your question, and gives you an answer grounded in the source text. It currently covers Apple, Microsoft, and Tesla for fiscal year 2025, which works out to 11,818 indexed chunks of filing text.

There are three tabs: Ask AI for questions, System Stats for a live look at what's loaded, and Financials for the revenue and earnings figures pulled out of each filing.

## How it works

When a filing comes in, it gets split into overlapping chunks of about a thousand tokens each. Every chunk is turned into a 384-dimension vector using the MiniLM sentence-transformer model and stored in pgvector, tagged with the company name and fiscal year. When you ask something, your question gets the same vector treatment, and a cosine-similarity search finds the closest passages, scoped to whichever company you asked about. Those passages and your question go to the language model, which writes the answer.

## Tech stack

Everything here is free or open-source.

| Layer | Local | Cloud |
|---|---|---|
| Language model | Llama 3 via Ollama | Llama 3.3 70B via Groq |
| Database | PostgreSQL 17 + pgvector | Neon (Postgres + pgvector) |
| Embeddings | sentence-transformers MiniLM (384-dim) | same |
| Backend | FastAPI | (UI calls RAG directly) |
| Interface | Streamlit | Streamlit Community Cloud |
| Data source | SEC EDGAR | same |

The local setup keeps everything on your machine and offline. The cloud version uses Groq and Neon because no free hosting tier has enough memory to run Ollama, which needs several gigabytes just to hold the model. The code picks the right backend automatically based on which environment variables are set, so the same codebase runs in both places.

## Companies and figures

These numbers were pulled out of the real FY2025 10-K filings by the language model. They're labeled experimental in the app because the extraction isn't perfect, so verify against the source before relying on them.

| Company | Ticker | Revenue (M) | Net income (M) | Diluted EPS |
|---|---|---|---|---|
| Apple | AAPL | 400,869 | 112,010 | 7.46 |
| Microsoft | MSFT | 279,009 | 101,832 | 13.64 |
| Tesla | TSLA | 97,690 | 3,794 | 1.08 |

## How accurate is it

There's an evaluation harness that runs 15 hand-checked question-answer pairs across the three companies, covering leadership, financials, and business questions. A local Llama 3 model acts as the judge. The latest run scored 14 out of 15, with answers coming back in about 7.3 seconds each on local hardware.

You can run it yourself:

```bash
python -m evaluation.run_eval
```

The one miss was Tesla's CFO, whose name sits in a certifications section that the retrieval step didn't surface for an income-statement-style query.

## Security

The `/ask` endpoint on the API requires an API key sent as an `X-API-Key` header, and it's rate-limited to 20 requests per minute per IP using slowapi. The read-only endpoints stay open so the data is easy to browse in a demo. All credentials, the database URL, the API key, and the Groq key, live in a `.env` file that's kept out of version control, loaded with python-dotenv.

## Logging

Every API request writes a structured JSON line to `logs/api.log` with a timestamp, the endpoint, how long it took, the detected company, a snippet of the answer, and whether it succeeded or errored. You can pull the recent entries through the API:

```bash
curl "http://127.0.0.1:8000/logs?n=20"
```

## Testing

There's a 36-test pytest suite covering the API endpoints, company detection, logging, chunking, and vector search. It runs in about six seconds and doesn't call the language model, since answer quality is measured separately by the evaluation harness.

```bash
python -m pytest tests/ -v
```

GitHub Actions runs this suite on every push to main, spinning up a Postgres container with pgvector. The data-dependent tests skip in CI since the CI database starts empty. The passing badge at the top of this file reflects the latest run.

## Running it locally

```bash
git clone https://github.com/PraveenKumarB-AI/financial-doc-intelligence.git
cd financial-doc-intelligence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need PostgreSQL 17 with pgvector and Ollama with Llama 3:

```bash
brew install postgresql@17
brew services start postgresql@17
psql -U $(whoami) -d postgres -c "CREATE DATABASE financial_rag;"
psql -U $(whoami) -d financial_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Ollama from https://ollama.com/download
ollama pull llama3
```

Create a `.env` file:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_rag
DB_USER=your_pg_user
DB_PASSWORD=
API_KEY=your-secret-key
```

Then set up the data and start it:

```bash
# Create the tables
psql -U $(whoami) -d financial_rag -f vectorstore/schema.sql

# Download and load each company
python -m ingestion.sec_downloader AAPL
python -m ingestion.ingest_company AAPL
# repeat for MSFT and TSLA

# Pull out the financial metrics
python -m vectorstore.financial_extractor

# Start the API (one terminal)
uvicorn api.app:app --reload

# Start the UI (another terminal)
streamlit run ui/streamlit_app.py
```

## Running it with Docker

The whole stack comes up with one command:

```bash
docker compose up -d --build
```

That starts three containers: Postgres with pgvector on 5432, the FastAPI service on 8000, and the Streamlit UI on 8501. The schema loads automatically on first start. The API container reaches Ollama on the host machine through `host.docker.internal`, so the model stays on the host and everything else is containerized.

Load the data into the containers:

```bash
docker compose exec api python -m ingestion.sec_downloader AAPL
docker compose exec api python -m ingestion.ingest_company AAPL
# repeat for MSFT and TSLA
docker compose exec api python -m vectorstore.financial_extractor
```

Stop everything with `docker compose down`. Don't run a local uvicorn or streamlit at the same time as the containers, since they'll fight over the same ports.

## Deploying to the cloud

The live version runs on Streamlit Community Cloud, which only runs the Streamlit app, no separate API server. So the UI calls the RAG functions directly instead of going through HTTP. The language model is Groq and the database is Neon, both free.

The steps, roughly: get a free Groq API key and a free Neon project with the vector extension enabled, load your data into Neon, then deploy the repo on Streamlit Community Cloud with `ui/streamlit_app.py` as the entry point and Python 3.11. The `GROQ_API_KEY` and `DATABASE_URL` go in the app's secrets manager rather than the `.env`, since `.env` isn't pushed to GitHub.

## API endpoints

| Endpoint | Method | Auth | What it does |
|---|---|---|---|
| `/` | GET | none | Health check |
| `/stats` | GET | none | Live knowledge-base stats |
| `/ask` | POST | API key + rate limit | Ask a question |
| `/metrics` | GET | none | Extracted financial metrics, optional `?company=` filter |
| `/companies` | GET | none | Companies with extracted metrics |
| `/logs` | GET | none | Recent request log entries, `?n=` to set count |

## Project layout

```
financial-doc-intelligence/
├── ingestion/          # download, parse, chunk, tag, embed, load
├── embeddings/         # MiniLM embedding generation
├── vectorstore/        # schema, DB connection, search, stats, extraction
├── rag/                # retrieval and the prompt-and-answer chain
├── llm/                # Ollama / Groq dual-backend client
├── analytics/          # company detection from question text
├── api/                # FastAPI app with auth and rate limiting
├── ui/                 # Streamlit interface
├── evaluation/         # gold Q&A set and the eval harness
├── logs/               # structured request logger
├── tests/              # pytest suite
├── .github/workflows/  # CI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## What's not perfect

Operating income and gross margin don't always get extracted cleanly. The model reliably finds revenue and net income, but the tabular layout for those other two trips it up sometimes. Microsoft's extracted revenue is about one percent off the real figure and Tesla's about three percent, which is why the numbers are marked experimental. On local hardware the language model runs on CPU, so answers take a few seconds to half a minute. The cloud version is much faster through Groq. And the API key in the repo is just a demo placeholder, so set a real one for any actual deployment.

## A note on the questions you can ask

```
Who is the CEO of Microsoft?
What was Tesla's revenue for FY2025?
What are Apple's main risk factors?
Who is the CFO of Apple?
What is Microsoft's main cloud product?
What does Tesla manufacture?
```

## Author

Praveen Kumar Botta — AI / ML Engineer
https://github.com/PraveenKumarB-AI

## License

MIT