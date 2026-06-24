# Financial Document Intelligence Assistant

**Live demo:** https://financial-doc-intelligence-gbnxwwhxj7d3fyqw4if6pn.streamlit.app

An AI assistant that reads SEC 10-K filings and answers plain-English questions about them. Ask it who runs a company, what its revenue was, or what risks it flagged, and it pulls the answer straight from the actual filing text instead of making something up.

It currently covers Apple, Microsoft, and Tesla for fiscal year 2025. Behind the scenes that's nearly 12,000 chunks of filing text, indexed so the assistant can find the right passage in a fraction of a second and answer from it.

## Why this exists

Annual reports are long, dense, and full of legal boilerplate. Finding one specific fact, like who the CFO is or what a company listed as its biggest risk, means scrolling through hundreds of pages. This tool does that searching for you and answers in seconds, and it always answers from the real document rather than from general knowledge, so you can trust that the response actually came from the filing.

## What it can do

Ask it questions in plain English and it answers from the filings. It automatically figures out which company you're asking about and only searches that company's documents. It also pulls key financial figures, revenue, net income, and earnings per share, out of each filing and shows them in a table. And it gives you a live view of exactly what's loaded into the system at any moment.

There are three tabs in the app: one for asking questions, one for system stats, and one for the financial figures.

## How it works

Think of it in two stages.

First, the setup. Each filing gets broken into small overlapping passages. Every passage is converted into a list of numbers, a "vector", that captures its meaning, and those vectors are stored in a special database built for fast similarity search. Each passage is also tagged with the company it came from and the fiscal year.

Then, when you ask a question, the same thing happens to your question, it becomes a vector. The system compares your question's vector against all the stored passages and pulls out the handful that are closest in meaning, narrowed down to the company you asked about. Those passages, plus your question, go to a language model, which reads them and writes a clear answer. This approach, finding relevant source text first and then answering from it, is called retrieval-augmented generation, or RAG. It's what keeps the answers grounded in the actual document.

## Two ways to run it

The project runs locally and in the cloud, and it's built to do both from the same code.

Run it locally and everything stays on your own machine and works offline: the language model runs through a tool called Ollama, and the database is PostgreSQL. Nothing is sent anywhere, and there are no costs.

The live version runs on the internet so anyone can use it. It swaps in two free hosted services, Groq for the language model and Neon for the database, because free web hosting doesn't have enough memory to run the local model, which needs several gigabytes just to load. The code detects which setup it's in and picks the right one automatically, so you never have to change anything by hand.

## What it's built with

Everything here is free or open-source.

| Part | Local | Live (cloud) |
|---|---|---|
| Language model | Llama 3 (via Ollama) | Llama 3.3 70B (via Groq) |
| Database | PostgreSQL + pgvector | Neon (Postgres + pgvector) |
| Meaning vectors | MiniLM sentence-transformer | same |
| Backend API | FastAPI | (the app calls the logic directly) |
| Interface | Streamlit | Streamlit Community Cloud |
| Filings source | SEC EDGAR (public, free) | same |

## The companies and their numbers

These figures were pulled out of the real FY2025 filings by the language model. They're marked experimental in the app because the extraction isn't flawless, so check them against the source filing before relying on them for anything serious.

| Company | Ticker | Revenue (millions) | Net income (millions) | Earnings per share |
|---|---|---|---|---|
| Apple | AAPL | 400,869 | 112,010 | 7.46 |
| Microsoft | MSFT | 279,009 | 101,832 | 13.64 |
| Tesla | TSLA | 97,690 | 3,794 | 1.08 |

## How well does it answer

The project includes a built-in test that asks 15 questions whose correct answers were checked by hand, spread across the three companies and covering leadership, financials, and business topics. On the latest run it got 14 of the 15 right, taking about seven seconds per question on a normal laptop. The single miss was Tesla's CFO, whose name appears in a part of the filing the search didn't reach for that kind of question.

You can run this check yourself with one command:

```bash
python -m evaluation.run_eval
```

## What's been built in

The system is more than just question-answering. It includes:

- Multi-company support, with answers automatically scoped to the right company
- Source-grounded answers that come from the filing text, not invented
- Automatic extraction of financial figures into a table
- A live stats view of what's loaded
- An accuracy test you can run anytime
- Structured logging of every request
- A 36-test automated test suite
- One-command Docker setup
- API key protection and rate limiting on the expensive endpoint
- Continuous integration that runs the tests on every code change
- A live public deployment

## Keeping it secure

The question-answering endpoint requires an API key and is limited to 20 requests a minute per user, so no single person can overload it. The browsing endpoints stay open so the data is easy to look at. All the secret values, database passwords and API keys, live in a local file that's deliberately kept out of the public code.

## Logging

Every request the system handles is written to a log file as a structured record: when it happened, what was asked, which company it was about, how long it took, and whether it worked. You can pull up the recent activity through the API.

## Testing

There's an automated test suite of 36 tests covering the API, company detection, logging, text chunking, and search. It runs in about six seconds. On top of that, GitHub automatically runs these tests every time the code changes, which is what the green badge at the top of this page shows. Answer quality is measured separately by the accuracy check described earlier.

```bash
python -m pytest tests/ -v
```

## Running it on your own machine

Clone the project and set up the environment:

```bash
git clone https://github.com/PraveenKumarB-AI/financial-doc-intelligence.git
cd financial-doc-intelligence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need PostgreSQL with the pgvector extension, and Ollama with the Llama 3 model:

```bash
brew install postgresql@17
brew services start postgresql@17
psql -U $(whoami) -d postgres -c "CREATE DATABASE financial_rag;"
psql -U $(whoami) -d financial_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Install Ollama from https://ollama.com/download, then:
ollama pull llama3
```

Create a file named `.env` with your settings:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_rag
DB_USER=your_postgres_user
DB_PASSWORD=
API_KEY=your-secret-key
```

Set up the data and start the app:

```bash
# Create the database tables
psql -U $(whoami) -d financial_rag -f vectorstore/schema.sql

# Download and load each company
python -m ingestion.sec_downloader AAPL
python -m ingestion.ingest_company AAPL
# repeat for MSFT and TSLA

# Pull out the financial figures
python -m vectorstore.financial_extractor

# Start the backend (in one terminal)
uvicorn api.app:app --reload

# Start the interface (in another terminal)
streamlit run ui/streamlit_app.py
```

Then open the address Streamlit prints, usually http://localhost:8501.

## Running it with Docker

If you'd rather not install everything by hand, the whole thing comes up with one command:

```bash
docker compose up -d --build
```

That starts three pieces together: the database, the backend, and the interface. The database tables are created automatically the first time. The language model still runs on your host machine, and the containers reach out to it.

Load the data in:

```bash
docker compose exec api python -m ingestion.sec_downloader AAPL
docker compose exec api python -m ingestion.ingest_company AAPL
# repeat for MSFT and TSLA
docker compose exec api python -m vectorstore.financial_extractor
```

Stop it all with `docker compose down`. Just don't run the local backend or interface at the same time as the containers, since they'll compete for the same ports.

## How the live version is deployed

The live site runs on Streamlit Community Cloud, which only runs the interface, not a separate backend. So in the cloud, the interface talks to the search-and-answer logic directly. The language model is Groq and the database is Neon, both on their free tiers.

In short: you get a free Groq key and a free Neon database, load your data into Neon, and deploy the project on Streamlit Community Cloud pointing at the interface file. The secret values go into Streamlit's own secrets manager rather than the local file, since the local file isn't part of the public code.

## The API, for developers

| Endpoint | Method | Needs a key? | What it returns |
|---|---|---|---|
| `/` | GET | no | A health check |
| `/stats` | GET | no | Live stats about what's loaded |
| `/ask` | POST | yes | An answer to your question |
| `/metrics` | GET | no | Extracted financial figures |
| `/companies` | GET | no | The companies that have figures |
| `/logs` | GET | no | Recent request activity |

## How the project is organized

```
financial-doc-intelligence/
├── ingestion/      Download, read, split, tag, and load the filings
├── embeddings/     Turn text into meaning vectors
├── vectorstore/    Database, search, stats, and figure extraction
├── rag/            Find relevant text and generate the answer
├── llm/            Talk to either Ollama or Groq
├── analytics/      Detect which company a question is about
├── api/            The backend, with key protection and rate limiting
├── ui/             The Streamlit interface
├── evaluation/     The accuracy check and its question set
├── logs/           Request logging
├── tests/          The automated test suite
├── .github/        Continuous integration setup
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Honest limitations

A few things worth knowing. The extraction of operating income and gross margin isn't always reliable, the model handles revenue and net income well but sometimes stumbles on those two because of how they're laid out in the tables. Microsoft's extracted revenue is off by about one percent and Tesla's by about three, which is why the figures are marked experimental. Running locally, the language model uses your CPU, so answers take a few seconds to half a minute; the cloud version is much faster. And the API key included in the code is just a placeholder, so set a real one before deploying anywhere that matters.

## Some questions you can try

```
Who is the CEO of Microsoft?
What was Tesla's revenue for FY2025?
What are Apple's main risk factors?
Who is the CFO of Apple?
What is Microsoft's main cloud product?
What does Tesla manufacture?
```

## Where the data comes from

All filings are from SEC EDGAR (https://www.sec.gov/edgar), which is public and free, with no API key required.

## Author

Praveen Kumar Botta — AI / ML Engineer
https://github.com/PraveenKumarB-AI

## License

MIT