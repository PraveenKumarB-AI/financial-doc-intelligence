CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id          SERIAL PRIMARY KEY,
    chunk_text  TEXT,
    metadata    JSONB,
    embedding   VECTOR(384),
    company     TEXT,
    source      TEXT,
    fiscal_year TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    id           SERIAL PRIMARY KEY,
    company      TEXT,
    fiscal_year  TEXT,
    metric_name  TEXT,
    metric_value TEXT,
    unit         TEXT,
    created_at   TIMESTAMP DEFAULT NOW()
);