CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (

    id SERIAL PRIMARY KEY,

    chunk_text TEXT,

    metadata JSONB,

    embedding VECTOR(384)

);