# ParseBench --- Document Parser Benchmarking Platform

An interactive platform for evaluating document parsers side by side,
with a focus on **extraction quality, table preservation, processing
latency, and reliability**.

ParseBench brings four parser integrations into one local web
application so users can upload a document, choose a parser, inspect the
extracted content, and review available performance metrics.

> **Status:** Local development application. It is not deployed as a
> hosted service.
>
> **Important:** Parser output quality depends on the document, scan
> quality, layout, parser configuration, and external-service
> availability. A successful parse does not guarantee correct
> extraction.

## Table of contents

-   [Highlights](#highlights)
-   [Supported parsers](#supported-parsers)
-   [Technology stack](#technology-stack)
-   [Architecture](#architecture)
-   [Requirements](#requirements)
-   [Local setup](#local-setup)
-   [Configure API credentials](#configure-api-credentials)
-   [Run the application](#run-the-application)
-   [Use the application](#use-the-application)
-   [Benchmark methodology and
    metrics](#benchmark-methodology-and-metrics)
-   [Project structure](#project-structure)
-   [Troubleshooting](#troubleshooting)
-   [Security](#security)
-   [Limitations and future
    improvements](#limitations-and-future-improvements)

## Highlights

-   **Interactive document upload:** Upload a supported document through
    the web interface.
-   **Parser selection:** Choose among LiteParse, Docling, LlamaParse,
    and Azure Document Intelligence.
-   **Extracted-output inspection:** Review the text or structured
    output returned by the selected parser.
-   **Latency reporting:** Inspect processing time for individual runs.
-   **Historical benchmark view:** Load saved benchmark metrics from CSV
    files in `results/`.
-   **Targeted invoice diagnostics:** Review selected invoice-field
    recovery and table-preservation checks where benchmark data is
    available.
-   **Local-first workflow:** Run the frontend and API on your own
    machine without deploying the application.

## Supported parsers

  -----------------------------------------------------------------------
  Parser                  Execution type          Notes
  ----------------------- ----------------------- -----------------------
  LiteParse               Local                   Invoked through the
                                                  `lit` command-line
                                                  interface. Local
                                                  package installation is
                                                  required.

  Docling                 Local                   Uses Docling's document
                                                  conversion
                                                  functionality. Its
                                                  dependencies can be
                                                  substantial.

  LlamaParse              Cloud API               Requires a valid Llama
                                                  Cloud API key and
                                                  network access.

  Azure Document          Cloud API               Requires an Azure
  Intelligence                                    Document Intelligence
                                                  endpoint and key.
  -----------------------------------------------------------------------

Supported file formats and parser-specific behaviour are defined by the
application configuration. Not every parser necessarily supports every
format or document feature.

**AWS Textract is not listed as a currently integrated parser in this
version of the README.** Add it to the supported-parsers list only after
its implementation has been completed and tested.

## Technology stack

-   **Frontend:** React, TypeScript, Vite
-   **Backend:** Python, FastAPI, Uvicorn
-   **Benchmark history:** CSV files
-   **Local parsing:** LiteParse, Docling
-   **Cloud parsing:** LlamaParse, Azure Document Intelligence

## Architecture

``` text
User
 |
 v
React + TypeScript frontend (Vite)
 |
 | HTTP requests / document upload
 v
FastAPI backend
 |
 +--> LiteParse CLI
 |
 +--> Docling
 |
 +--> LlamaParse API
 |
 +--> Azure Document Intelligence API
 |
 v
Extracted output + run metrics
```

Historical benchmark metrics are read from saved CSV files. The frontend
communicates with the backend API; parser execution and result handling
are performed by the backend.

## Requirements

Install the following before starting:

-   Git
-   Python 3.10 or a compatible version supported by the project's
    parser dependencies
-   Node.js and npm
-   Internet access for installing packages and using cloud-based
    parsers
-   API credentials for the cloud parsers you plan to use

**Platform note:** The commands below use a Bash shell, such as WSL
Ubuntu on Windows or Linux. Local parser dependencies may require
additional system libraries and disk space.

## Local setup

### 1. Clone the repository

``` bash
git clone https://github.com/himanshu-shekhar2327/ParseBench.git
cd ParseBench
```

If you already cloned the repository, navigate to its directory instead.

### 2. Create and activate a Python virtual environment

Run these commands from the repository root:

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install backend dependencies:

``` bash
pip install -r requirements.txt
```

If installation fails, check the Python version and the error message
for the specific parser dependency. Some local parsing libraries have
large dependencies and may need additional system packages.

### 3. Configure environment variables

Create a local `.env` file from the example:

``` bash
cp .env.example .env
```

Open `.env` and fill in the values required for the cloud parsers you
intend to use. See [Configure API
credentials](#configure-api-credentials).

Do not commit `.env`.

### 4. Install frontend dependencies

Open a second terminal, then run:

``` bash
cd frontend
npm install
```

## Configure API credentials

The cloud integrations use environment variables configured for the
backend. The current documented variable names are:

``` dotenv
LLAMA_CLOUD_API_KEY=replace_with_your_llama_cloud_key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=replace_with_your_azure_key
```

These are **placeholders, not real credentials**. Use the exact variable
names expected by the implementation and `.env.example`.

-   LiteParse and Docling may be run locally, but their package and
    system requirements must be installed.
-   LlamaParse requires a valid Llama Cloud API key.
-   Azure Document Intelligence requires a valid endpoint and key.
-   AWS Textract credentials should be configured only if an AWS
    Textract integration is implemented and the project is explicitly
    configured to use it.

If a cloud key is unavailable, the corresponding parser may fail. Cloud
provider usage may incur charges.

## Run the application

Keep the backend and frontend running in separate terminals.

### Terminal 1 --- Backend

From the repository root, with `.venv` activated:

``` bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Useful backend URLs:

-   **API health check:** http://127.0.0.1:8000/api/health
-   **Interactive API documentation:** http://127.0.0.1:8000/docs
-   **Historical benchmark summary:**
    http://127.0.0.1:8000/api/benchmark/summary

The health endpoint should return a JSON response indicating that the
service is healthy.

### Terminal 2 --- Frontend

From the repository root:

``` bash
cd frontend
npm run dev
```

Open the local URL printed by Vite. The default is usually:

http://localhost:5173

If port `5173` is already in use, Vite may select another port, such as
`5174`. Use the exact URL printed in the terminal. The backend's CORS
configuration must allow the frontend origin you use.

## Use the application

1.  Open the local frontend URL.
2.  Upload a supported document. The current API enforces a 20 MB upload
    limit.
3.  Select a parser.
4.  Select an output format if the interface offers one.
5.  Start the parsing run.
6.  Inspect the extracted output and reported processing metrics.
7.  Use the historical benchmark section to review saved results where
    available.

Use documents you are authorized to process. Review extracted content
before relying on it for business or financial decisions.

## Benchmark methodology and metrics

ParseBench separates several evaluation dimensions because they measure
different things.

  -----------------------------------------------------------------------
  Metric                  What it indicates       What it does not prove
  ----------------------- ----------------------- -----------------------
  Processing latency      Time taken for a        That the output is
                          recorded parsing run    accurate

  Run availability /      Whether a parser        That the extracted
  success                 completed, failed, or   content is correct
                          was unsupported in the  
                          recorded benchmark      

  Field recovery          Whether expected fields That every value is
                          were found in a         exact or associated
                          targeted test           with the correct field

  Table preservation      Whether targeted        General table accuracy
                          outputs retained the    across all documents
                          required table          
                          structure               

  Qualitative output      Readability, ordering,  A standardized numeric
  review                  corruption, and visible accuracy score
                          structure issues        
  -----------------------------------------------------------------------

### Interpreting results responsibly

-   Individual timings captured from a single run are observations, not
    repeated-trial performance estimates.
-   Saved corpus-level results measure availability and latency unless a
    separate ground-truth scoring process was performed.
-   Targeted synthetic-invoice field and table checks are diagnostic
    tests; they should not be presented as overall parser accuracy.
-   Different sample sizes or denominators should be stated clearly and
    should not be treated as directly equivalent.
-   A value appearing in extracted text does not prove it was assigned
    to the correct row, column, transaction, or field.
-   Metrics that were not measured should be reported as unavailable,
    not estimated.

For a stronger future evaluation, use a fixed document set, verified
ground-truth annotations, consistent parser configurations, multiple
timing trials, explicit sample sizes, and separate scoring for field
values, table cells, reading order, and text error rates where a
reliable reference transcription exists.

## Project structure

The main areas of the repository are expected to include:

``` text
ParseBench/
├── backend/                 # FastAPI application and backend logic
├── frontend/                # React + TypeScript + Vite application
├── parsers/                 # Parser-specific integration code, where applicable
├── results/                 # Saved benchmark CSV files
├── requirements.txt         # Python dependencies
├── .env.example             # Safe template for environment variables
├── .gitignore
└── README.md
```

The exact files may evolve as the project changes. Use the repository
tree as the source of truth if a directory or file differs.

## Troubleshooting

### The frontend says "Failed to fetch"

1.  Confirm the backend is running.
2.  Open http://127.0.0.1:8000/api/health.
3.  Check the browser's Developer Tools → **Network** tab for the
    failing request and response.
4.  Check that FastAPI's CORS allowlist includes the frontend origin,
    including the port (for example, `http://localhost:5173` or
    `http://localhost:5174`).

### Port 5173 is already in use

Vite may choose another port. Open the URL shown in its terminal and
make sure the backend CORS configuration allows that origin.

### A parser fails or appears to hang

1.  Check the backend terminal for the actual exception or subprocess
    output.
2.  Verify that the document is valid, supported, and below the upload
    limit.
3.  Confirm local parser packages and command-line tools are installed.
4.  For cloud parsers, verify credentials, endpoint, network access,
    quotas, service status, and billing configuration.
5.  Do not assume a generic frontend error proves that the uploaded
    document is corrupt; inspect the backend response and logs.

### Historical benchmark metrics fail to load

Confirm that the expected CSV files exist in `results/` and that the
backend can read them. Check the backend logs and browser Network tab
for the precise error.

## Security

-   **Never commit `.env` or real credentials.**
-   Commit `.env.example` only with placeholder values.
-   Do not put API keys in frontend code: frontend variables can be
    exposed to users.
-   Use least-privilege cloud credentials and follow your organization's
    approved secret-sharing process.
-   If a real key has been committed or exposed, revoke or rotate it;
    deleting it from the latest commit is not enough.
-   Treat uploaded documents and extracted text as potentially
    sensitive.
-   Check `git status` and staged files before committing:

``` bash
git status
git diff --cached
```

## Limitations and future improvements

Possible next steps include:

-   Add a verified AWS Textract integration if required.
-   Standardize the ground-truth test set and scoring procedure.
-   Add repeated latency trials and clearer reporting of sample sizes.
-   Expand field-level and table-cell evaluation.
-   Improve parser error reporting and progress feedback for
    long-running requests.
-   Document tested operating-system and dependency versions for
    reproducibility.

These are potential improvements, not claims that the features are
already implemented.
