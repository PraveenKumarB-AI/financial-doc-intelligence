# Financial Document Intelligence Assistant

## Overview

Financial Document Intelligence Assistant is an AI-powered system designed to download, process, analyze, and query SEC financial filings using Retrieval-Augmented Generation (RAG).

This project will ultimately enable users to ask natural language questions about public company financial reports and receive accurate, source-grounded answers.

---

## Project Roadmap

### Module 1: SEC Filing Downloader ✅

Download SEC filings (10-K, 10-Q, 8-K) from the SEC EDGAR database.

### Module 2: PDF Processing & Text Extraction

Extract text from downloaded filings using PyMuPDF.

### Module 3: Intelligent Chunking Engine

Split large financial documents into semantic chunks.

### Module 4: Embedding Pipeline

Generate vector embeddings from document chunks.

### Module 5: Vector Database

Store embeddings in a vector database for retrieval.

### Module 6: Financial RAG System

Retrieve relevant financial information based on user queries.

### Module 7: LLM-Powered Financial Assistant

Answer financial questions using retrieved SEC filing data.

---

## Current Module

### Module 1: SEC Filing Downloader

This module downloads SEC filings from the EDGAR database and stores them locally for downstream processing.

### Features

- Download SEC filings automatically
- Support for public companies
- Organized local storage
- Foundation for financial document analysis

---

## Project Structure

```text
financial-doc-intelligence/
│
├── ingestion/
│   └── sec_downloader.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-doc-intelligence.git
cd financial-doc-intelligence
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Environment

Mac/Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Dependencies

- sec-edgar-downloader
- pymupdf
- langchain
- python-dotenv
- pandas
- tqdm

---

## Example Usage

Run:

```bash
python ingestion/sec_downloader.py
```

Example Output:

```text
Downloading Apple filings...
Download completed.
```

---

## Data Source

SEC EDGAR Database

https://www.sec.gov/edgar

---

## Future Enhancements

- Multi-company downloads
- Automated filing updates
- Financial statement extraction
- Semantic search
- RAG-based financial chatbot
- Streamlit web application

---

## Author

Praveen Kumar Botta

AI / ML Engineer

---

## License

MIT License