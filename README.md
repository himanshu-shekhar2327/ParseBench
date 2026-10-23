# Parsebench

An interactive document parser benchmarking platform comparing LiteParse, Docling, LlamaParse, and Azure Document Intelligence on extraction quality, table preservation, processing speed, and reliability.

## Features

- Upload documents and compare parser outputs.
- Run local parsers (LiteParse and Docling) and cloud parsers (LlamaParse and Azure Document Intelligence).
- View historical benchmark metrics from saved CSV results.
- Inspect extraction output and processing latency.
- Evaluate selected invoice fields and table preservation.

## Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Python
- Benchmark history: CSV files
- Parsers: LiteParse, Docling, LlamaParse, Azure Document Intelligence

## Setup

### 1. Backend

Use Python 3.10 or a compatible version supported by the parser dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your own credentials to `.env`:

- `LLAMA_CLOUD_API_KEY`
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

Never commit `.env` or share its contents.

Start the backend from the repository root:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/api/health

### 2. Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Benchmark Results

Historical benchmark CSV files are stored in `results/`. The document corpus and generated parser outputs are excluded from Git to keep the repository lightweight. Supply your own test documents locally.

Some field-recovery and table-preservation metrics are based on targeted synthetic-invoice tests. They are not overall accuracy scores across all document types. Metrics that have not been measured are reported as unavailable rather than estimated.

Cloud parser calls may incur usage charges.

## Security

- Never commit API keys or `.env` files.
- Review documents and extracted text before sharing.
- Keep cloud credentials private.
