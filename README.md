# cClyptus.AI — SAP BRIM Enterprise Knowledge Assistant

cClyptus.AI is an enterprise-grade Retrieval-Augmented Generation (RAG) assistant purpose-built for **SAP Billing and Revenue Innovation Management (BRIM)**. It delivers grounded, auditable technical guidance across high-volume subscription, rating, billing, and financial sub-ledger architectures while strictly enforcing domain boundaries, claim-level citation verification, and enterprise intellectual property governance.

---

## 1. Project Overview & Architecture

### Core Purpose
SAP BRIM implementations integrate multiple high-throughput components to monetize recurring and usage-based business models. cClyptus.AI provides specialized engineering assistance for SAP consultants, architects, and developers by extracting verified facts from official SAP documentation and partner publications, rejecting hallucinations, and flagging unverified technical claims.

### Supported SAP BRIM Modules
- **Subscription Order Management (SOM)**: Master data modeling, Business Partners (`BUT000`), Contract Accounts (`FKKVKP`), provider contracts (`EVER`), Order Distribution Infrastructure (ODI), and subscription lifecycles.
- **Convergent Charging (CC)**: Real-time rating, allowance plans, charge plans, BART batch rating, subscriber accounts, Core Tool pricing trees, and partition architectures.
- **Convergent Invoicing (CI)**: Consumption Item (CIT) and Billable Item (BIT) data models (`DFKKBIXCIT*`, `DFKKBIXBIT*`), billing processes, invoicing execution, aggregation, and reversal.
- **Contract Accounts Receivable and Payable (FI-CA)**: High-volume sub-ledger accounting, document headers (`DFKKKO`), open items (`DFKKOP`), payments, dunning, clearing, and General Ledger reconciliation (`ACDOCA` / `BSEG`).
- **Revenue Accounting and Reporting (RAR)**: IFRS 15 / ASC 606 revenue recognition, performance obligations (POB), contract liability, and asset posting.
- **Convergent Mediation (CM) & Integration**: Mediation feeds, SAP Cloud Integration (CPI), SAP Process Orchestration (PO), REST/OData APIs, RFC interfaces, and asynchronous distribution.

### High-Level Architecture Flow
```
User Query
    │
    ├── 1. Query Resolution & Scope Guardrail (sap_classifier.py rejects non-SAP queries)
    │
    ├── 2. Hybrid Retrieval (BM25 Lexical + 384-dim Dense Vector Search on document_chunks)
    │
    ├── 3. Cross-Encoder Reranking (reranking_service.py: ms-marco-MiniLM-L-6-v2)
    │
    ├── 4. Evidence Confidence & Source Comparative Selection (multi_source_compare.py)
    │      ├── Stage 1: Official SAP Knowledge Base (Authoritative Tier 1/2)
    │      ├── Stage 2: Isolated GitHub Repository Retrieval (Gated by REPO_SOURCE_ENABLED)
    │      └── Stage 3: Tavily Web Search Fallback (Triggered only when internal score < 0.6761)
    │
    ├── 5. Answer Planning & LLM Generation (llm_service.py with automatic provider failover)
    │
    ├── 6. Claim Grounding Verification Gate (grounding_service.py: 80% publication threshold)
    │      ├── Automated Claim Verification against retrieved chunks
    │      ├── Technical Identifier Audit (SPRO paths, tables, T-codes validated)
    │      └── Controlled Repair Loop (re-prompts LLM if ungrounded claims are detected)
    │
    └── 7. Streaming Response & Citation Generation (FastAPI SSE -> React 19 Frontend)
```

---

## 2. Technology Stack

### Backend
- **Runtime**: Python 3.10+ (Tested through Python 3.14)
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database / ORM**: SQLAlchemy 2.0 with dual-engine support:
  - **Zero-Configuration Default**: Local SQLite database with embedding BLOBs (`backend/sap_assistant.db`)
  - **Enterprise Scale**: PostgreSQL 16 with `pgvector` extension
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **Reranker Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **LLM Engine**: Multi-tier failover orchestrator:
  - Primary: Groq API (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`)
  - Secondary / Local: OpenAI API (`gpt-4o-mini`, `gpt-4o`)
- **Web Retrieval**: Tavily Search API (restricted to official `*.sap.com` domains)

### Frontend
- **Framework**: React 19.2 + TypeScript (Vite 8.3 build system)
- **Styling**: Tailwind CSS 4.3 + Lucide Icons + Framer Motion
- **Markdown & Code Rendering**: React Markdown 10 + Remark GFM
- **Routing**: React Router 7 (Single Page Application)
- **Linter**: Oxlint (fast Rust-based linter)

---

## 3. Prerequisites

Before setting up cClyptus.AI, ensure the following software is installed:
- **Python**: Version 3.10 or higher (`python --version`)
- **Node.js**: Version 18.x or higher (`node --version`)
- **npm**: Version 9.x or higher (`npm --version`)
- **Git**: Version 2.30 or higher (`git --version`)
- **Docker** *(Optional)*: Required only if running PostgreSQL with pgvector container. The included SQLite database runs out-of-the-box without Docker.

---

## 4. Installation

Clone the repository and install both backend and frontend dependencies:

### 1. Backend Installation
From the repository root (`SAP_BRIM`):
```bash
# Optional: Create and activate a Python virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install Python requirements
pip install -r backend/requirements.txt
```

### 2. Frontend Installation
In a separate terminal or the same environment:
```bash
cd frontend
npm install
cd ..
```

---

## 5. Environment Configuration

cClyptus.AI includes a safe environment template at [`backend/.env.example`](file:///c:/Users/yuvar/OneDrive/Desktop/gen%20ai%20and%20agentic%20ai/super%20admin%20portal/SAP/SAP_BRIM/backend/.env.example). Copy it to `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

### Key Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///backend/sap_assistant.db` | Database connection string (SQLite or PostgreSQL) |
| `JWT_SECRET` | *Random secret string* | Secret key used to sign session JWTs |
| `ADMIN_API_KEY` | *Secret API key* | API key for administrative ingestion routes |
| `LLM_PROVIDER` | `groq` | Primary LLM provider (`groq`, `openai`, or `local`) |
| `GROQ_API_KEY` | `""` | API key for Groq inference (Tier 1) |
| `OPENAI_API_KEY` | `""` | API key for OpenAI fallback (Tier 2) |
| `WEB_FALLBACK_ENABLED` | `true` | Enables approved SAP web search when document or evidence confidence is weak |
| `DOCUMENT_MATCH_THRESHOLD` | `0.80` | Triggers GitHub and SAP web comparison when the best document rerank score is below 80% |
| `AUTO_MULTI_SOURCE_FALLBACK` | `true` | Automatically compares eligible document, GitHub, and web evidence when document confidence is weak |
| `ANSWER_TEMPERATURE` | `0.10` | Low generation temperature for factual answers; runtime caps this setting at `0.30` |
| `TAVILY_API_KEY` | `""` | API key for authoritative Tavily SAP web search |
| `REPO_SOURCE_ENABLED` | `false` | **Feature Flag**: Activates GitHub repository retrieval |
| `MULTI_SOURCE_COMPARE_ENABLED` | `false` | **Feature Flag**: Activates multi-source comparative ranking |
| `SAP_WEB_SOURCES_ENABLED` | `false` | **Feature Flag**: Activates extended official web and community sources |

> [!IMPORTANT]
> Never commit your `backend/.env` file with actual API keys or credentials. The legacy repository and comparison flags remain off by default; automatic multi-source fallback is controlled separately by `AUTO_MULTI_SOURCE_FALLBACK`.

---

## 6. Database Setup

### Local SQLite (Zero-Config Default)
The repository includes a pre-indexed SQLite vector database at [`backend/sap_assistant.db`](file:///c:/Users/yuvar/OneDrive/Desktop/gen%20ai%20and%20agentic%20ai/super%20admin%20portal/SAP/SAP_BRIM/backend/sap_assistant.db). At the consolidation audit it contained **11,317 chunks across 40 historical document records**; the current source inventory contains 30 PDFs. Use the authenticated `GET /api/rag-inspect/documents` endpoint for the live source/index reconciliation before an ingestion run. No database initialization commands are required when running with SQLite.

### PostgreSQL with pgvector (Enterprise Docker Setup)
If running under PostgreSQL:
1. Start the pgvector container via Docker Compose:
   ```bash
   docker-compose up -d
   ```
2. Update `DATABASE_URL` in `backend/.env`:
   ```ini
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sap_assistant
   ```
3. Migrate existing vectors from SQLite to PostgreSQL:
   ```bash
   python backend/scripts/migrate_sqlite_to_pgvector.py
   ```

---

## 7. Knowledge Base & Document Ingestion

The active knowledge base has one canonical source location: `knowledge_base/documents/`. It contains the SAP courseware, product documentation, SAP Press books, and the locally authored guides used by the ingestion pipeline.

### To Re-Ingest or Add Documents:
1. Place new PDF documents into `knowledge_base/documents/`.
2. Run the structure-aware chunking and embedding pipeline:
   ```bash
   python -m backend.app.ingestion.ingest
   ```
The ingestion process automatically:
- Extracts headings, hierarchy, and tables from PDFs.
- Generates 384-dimensional embeddings via SentenceTransformers.
- Audits technical identifiers against the 638-identifier index.
- Commits chunks with authority tier tags to `document_chunks`.

---

## 8. Starting the Application

Run the backend and frontend in two separate terminal windows:

### Terminal 1: Backend Server (FastAPI)
From the repository root (`SAP_BRIM`):
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

### Terminal 2: Frontend Client (Vite + React 19)
From the `SAP_BRIM/frontend` directory:
```bash
cd frontend
npm run dev
```
- **Application UI**: [http://localhost:5173](http://localhost:5173)
- All `/api/*` requests are proxied to the backend at `http://localhost:8000`.

### Production Frontend Build
To create optimized static assets:
```bash
cd frontend
npm run build
```

---

## 9. Testing & Evaluation

### 1. Run Complete Automated Test Suite (73 Tests)
From the repository root:
```bash
python -m pytest backend/tests -v
```
Runs all 10 test modules:
- `test_auth_and_isolation.py`: User registration, JWT security, multi-tenant session isolation.
- `test_followup_and_greetings.py`: Query rewriting, greeting detection, conversational assistant.
- `test_grounded_contract_and_packing.py`: Context budget packing, system prompt glossary injection, rate limiting.
- `test_phase1_corpus_and_metadata.py`: Authority tiers, 638-identifier index hash, SPDX license gates.
- `test_rag_and_citations.py`: End-to-end RAG retrieval, citation generation.
- `test_rag_pipeline_v2.py`: Web fallback, 80% claim grounding verification, SSE streaming stages.
- `test_repo_retrieval_and_comparison.py`: Feature flag safety, BRIM relevance gate, multi-source comparison, citations.
- `test_sap_restriction.py`: SAP domain classifier, rejection of out-of-scope non-SAP inquiries.
- `test_security.py`: Admin endpoint authorization, denial of document download routes.
- `test_technical_accuracy_and_db.py`: Real vs fabricated SAP identifiers, thread-safe caching.

### 2. Run Shadow-Mode Benchmark on Development Dataset
To evaluate the multi-source comparator across the 132-question development dataset:
```bash
python backend/evaluation/run_shadow_evaluation.py
```
*Note*: This evaluation strictly utilizes `backend/evaluation/datasets/dev_questions.jsonl`. The sealed 96-question held-out dataset (`heldout_questions.jsonl`) is protected and remains untouched.

---

## 10. GitHub Retrieval & Multi-Source Comparison

cClyptus.AI compares retrieved document evidence with approved GitHub repository chunks and SAP web results when the best document rerank score is below 0.80 (or the evidence-confidence gate requests fallback). It selects the eligible candidate with the highest relevance score after source-authority weighting. GitHub candidates are limited to repository chunks already ingested with an approved license and passed BRIM relevance checks.

### Multipart SAP questions and evidence boundaries

Clear multi-part requests are retrieved and reranked part by part. Each part is carried with its own evidence label; a part with no internal match receives a non-citable retrieval-gap marker, and low-scoring parts can trigger GitHub and SAP web fallback independently. The web search prefers `help.sap.com`, broadening to other approved SAP properties only when Help Portal search returns no results. Product/release metadata is used when supplied by the question or present in a source; the system does not infer a source release when metadata is absent.

Answers should preserve supported parts and calculations based on explicit assumptions, while separating verified SAP-standard behavior, customer-specific configuration, illustrative calculations, and unresolved details. A missing retrieval match is not proof that SAP lacks a feature. For billing, service period, charge period, billable item, billing document, invoicing document, and FI-CA posting document remain distinct; no end-to-end connection is asserted unless retrieved evidence establishes it. Material SAP-specific claims must cite retrieved source metadata, and the system must not fabricate identifiers, citations, or implementation sequences.

Set `AUTO_MULTI_SOURCE_FALLBACK=false` to disable automatic comparison. `WEB_FALLBACK_ENABLED=false` disables live SAP web search. GitHub lookup requires previously ingested, approved repository chunks in the repository index.

### Operating Modes & Feature Flags
Controlled via environment variables in `backend/.env`:

1. **Mode A — Legacy Feature Flags (Default)**:
   ```ini
   REPO_SOURCE_ENABLED=false
   MULTI_SOURCE_COMPARE_ENABLED=false
   ```
   - Explicit shadow/comparison flags are disabled.
   - Automatic low-confidence fallback remains enabled unless `AUTO_MULTI_SOURCE_FALLBACK=false`.

2. **Mode B — Repository Shadow Mode**:
   ```ini
   REPO_SOURCE_ENABLED=true
   MULTI_SOURCE_COMPARE_ENABLED=false
   ```
   - Legacy knowledge base remains the authoritative response path.
   - Retrieves repository candidates in a separate shadow branch for logging and audit.
   - Zero output mutation, zero user-visible changes.

3. **Mode C — Multi-Source Comparison Mode**:
   ```ini
   REPO_SOURCE_ENABLED=true
   MULTI_SOURCE_COMPARE_ENABLED=true
   ```
   - Compares evidence across Knowledge Base, GitHub Repositories, and Web Search.
   - Evaluates evidence using the score-based authority model:
     $$\text{final\_score} = \text{calibrated\_relevance\_score} \times \text{source\_authority\_weight}$$
   - Clears candidates through the mandatory BRIM relevance gate and acceptance threshold ($0.6761$).

### Repository Ingestion Command
To scan and ingest configured repositories:
```bash
python backend/scripts/ingest_github_repositories.py
```

### Automated Rollback & Verification Command
To verify system health or safely restore legacy behavior:
```bash
python backend/scripts/rollback_github_retrieval.py
```
To purge repository records from `github_repo_chunks` while leaving the knowledge-base chunks intact:
```bash
python backend/scripts/rollback_github_retrieval.py --purge-repo-chunks
```

---

## 11. Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **`Unauthorized: missing or invalid API key`** | Missing or expired `GROQ_API_KEY` or `OPENAI_API_KEY` | Provide a valid API key in `backend/.env`. |
| **Database connection fails** | PostgreSQL server not running when `DATABASE_URL` is set to Postgres | Start Docker container with `docker-compose up -d`, or switch `DATABASE_URL=sqlite:///backend/sap_assistant.db`. |
| **`429 Rate Limit Reached` on LLM** | Primary LLM provider rate limit reached | The built-in failover mechanism automatically retries across configured secondary models in `llm_service.py`. |
| **`Port 8000 already in use`** | A lingering Uvicorn process is occupying port 8000 | Terminate the existing process or run Uvicorn on another port with `--port 8001`. |
| **Query rejected as "out of scope"** | Query is non-SAP or conversational | By design, cClyptus.AI rejects general-knowledge questions to prevent hallucinations outside SAP BRIM. |
| **Frontend fails to connect to backend** | Backend server is not running at `http://localhost:8000` | Start the backend server with `uvicorn backend.app.main:app --port 8000`. |

---

## 12. Project Structure

```text
SAP_BRIM/
├── README.md                           # Master setup, architectural, and operational documentation
├── docker-compose.yml                  # Optional PostgreSQL + pgvector container definition
├── pytest.ini                          # Pytest configuration and path settings
│
├── backend/                            # FastAPI Backend Application
│   ├── .env.example                    # Safe environment template
│   ├── requirements.txt                # Python package dependencies
│   ├── sap_assistant.db                # Pre-indexed SQLite corpus; inspect endpoint reports live counts
│   │
│   ├── app/                            # Application Core
│   │   ├── main.py                     # FastAPI entrypoint, middleware, and route mounting
│   │   ├── config.py                   # Pydantic application settings & feature flags
│   │   ├── database.py                 # SQLAlchemy engine, session management, dual-dialect support
│   │   ├── api/                        # REST and SSE API endpoints (chat, auth, health, ingestion)
│   │   ├── corpus/                     # Tier definitions (official_sap, partner) and 638-ID index
│   │   ├── ingestion/                  # Structure-aware chunking and document ingestion
│   │   ├── models/                     # SQLAlchemy models (DocumentChunk, GithubRepoChunk, User, Chat)
│   │   ├── prompts/                    # System prompts, role definitions, grounding rules
│   │   ├── retrieval/                  # Source registry, multi-source comparator, relevance gate, web doc ingest
│   │   ├── schemas/                    # Pydantic response contracts and citation schemas
│   │   ├── security/                   # Password hashing, JWT token generation, RBAC
│   │   └── services/                   # RAG service, embeddings, reranking, LLM failover, grounding
│   │
│   ├── data/                           # Data storage
│   │   ├── github_snapshots/           # Local repository snapshots preserving upstream licenses
│   │   └── web_doc_snapshots/          # Snapshots of official SAP documentation and community chunks
│   │
│   ├── evaluation/                     # Evaluation benchmark suite
│   │   ├── datasets/                   # Evaluation splits (dev_questions.jsonl & heldout_questions.jsonl)
│   │   ├── results/                    # Machine-readable evaluation benchmarks and summaries
│   │   ├── run_evaluation.py           # Evaluation runner
│   │   └── run_shadow_evaluation.py    # Shadow-mode evaluation on 132 dev questions
│   │
│   ├── scripts/                        # Management & Migration Scripts
│   │   ├── calibrate_retrieval_threshold.py  # Gate threshold calibration script
│   │   ├── discover_github_repositories.py   # GitHub organizational repository candidate discovery
│   │   ├── ingest_github_repositories.py     # Reproducible GitHub repository ingestion pipeline
│   │   ├── ingest_sap_web_sources.py         # Official SAP documentation & community ingestion pipeline
│   │   ├── migrate_sqlite_to_pgvector.py     # Database vector migration script
│   │   ├── rollback_github_retrieval.py      # Non-destructive rollback and governance audit script
│   │   └── run_real_samples.py               # Sample query execution benchmark
│   │
│   └── tests/                          # Automated Pytest Suite
│       ├── test_auth_and_isolation.py
│       ├── test_followup_and_greetings.py
│       ├── test_grounded_contract_and_packing.py
│       ├── test_phase1_corpus_and_metadata.py
│       ├── test_rag_and_citations.py
│       ├── test_rag_pipeline_v2.py
│       ├── test_repo_retrieval_and_comparison.py
│       ├── test_source_registry_and_web_sources.py
│       ├── test_sap_restriction.py
│       ├── test_security.py
│       └── test_technical_accuracy_and_db.py
│
├── frontend/                           # React 19 + TypeScript + Vite Web Client
│   ├── package.json                    # Frontend package dependencies and build scripts
│   ├── package-lock.json               # Locked dependency tree
│   ├── vite.config.ts                  # Vite build and proxy configuration
│   ├── tailwind.config.js              # Tailwind styling configuration
│   ├── index.html                      # HTML application template
│   └── src/                            # Application source code
│       ├── main.tsx                    # React client entrypoint
│       ├── App.tsx                     # Main application layout and routes
│       ├── components/                 # UI components (chat, citations, markdown, follow-ups)
│       ├── context/                    # Auth and session context providers
│       ├── layouts/                    # Navigation and app layout wrappers
│       ├── pages/                      # Page views (ChatPage, LoginPage, RegisterPage, AdminPage)
│       └── services/                   # SSE streaming client and REST API service calls
│
└── knowledge_base/                     # SAP BRIM source documents
    └── documents/                      # Canonical source folder (30 PDFs at consolidation audit)
```
