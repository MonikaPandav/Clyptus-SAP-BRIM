# Clyptus.AI — SAP BRIM Enterprise Knowledge Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019-61DAFB.svg?style=flat&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

**Clyptus.AI** is an enterprise-grade AI Solution Architect and Retrieval-Augmented Generation (RAG) assistant purpose-built for **SAP Billing and Revenue Innovation Management (BRIM)**, SAP S/4HANA, and enterprise billing systems.

It combines hybrid dense vector search, BM25 lexical retrieval, cross-encoder reranking, multi-tier LLM streaming, strict claim grounding, and a secure **Role-Based Admin Control Center**.

---

## 🚀 Quick Start Guide (Run on Any Laptop in 5 Minutes)

Follow these steps to run the complete system locally on Windows, macOS, or Linux.

### Prerequisites

Make sure the following are installed on your machine:
* **Python 3.10+** (tested up to Python 3.14): [Download Python](https://www.python.org/downloads/)
* **Node.js 18+ & npm 9+**: [Download Node.js](https://nodejs.org/)
* **Docker Desktop** (runs the PostgreSQL + pgvector database): [Download Docker](https://www.docker.com/products/docker-desktop/)
* **Git**: [Download Git](https://git-scm.com/)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Clyptus-Soft/SAP_BRIM_Ai.git
cd SAP_BRIM_Ai
```

---

### Step 2: Start the Database (PostgreSQL + pgvector in Docker)

PostgreSQL with the pgvector extension is the application's **only** database. It stores documents, chunks, 384-dimensional embeddings, users, chats and citations. There is no SQLite or other fallback; if PostgreSQL is unreachable the backend refuses to start with a clear error.

1. **Create the Compose settings file** at the repository root and set two passwords:
   * **Windows (PowerShell)**: `Copy-Item .env.example .env`
   * **macOS / Linux**: `cp .env.example .env`

   `SAP_BRIM_DB_PASSWORD` is the application's database password (it must match `DATABASE_URL` in `backend/.env`, see Step 3). `POSTGRES_HOST_PORT` (default `5435`) is the host port.

2. **Start PostgreSQL**:
   ```bash
   docker compose up -d postgres
   ```
   This starts the `sap_assistant_postgres` container (`pgvector/pgvector:pg16`) on `127.0.0.1:5435`. On a new volume it creates the `sap_brim_ai` role and database with the `vector` extension (`docker/postgres/init/`); the backend creates tables and indexes on startup.

> [!WARNING]
> The container and its `sap_projects_pgdata` volume are shared with the sibling SAP_Projects stack (whose `sap_assistant` database lives in the same server). Never run `docker compose down -v`: it deletes the volume and every database in it.

---

### Step 3: Set Up Backend

1. **Create and activate a Python virtual environment**:
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux (Bash/Zsh)**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file:
   * **Windows (PowerShell)**:
     ```powershell
     Copy-Item backend/.env.example backend/.env
     ```
   * **macOS / Linux**:
     ```bash
     cp backend/.env.example backend/.env
     ```

   Set `DATABASE_URL` to the application database, using the password from the root `.env`:
   ```ini
   DATABASE_URL=postgresql://sap_brim_ai:<SAP_BRIM_DB_PASSWORD>@127.0.0.1:5435/sap_brim_ai
   ```
   (A backend running inside the Compose network would use `postgres:5432` instead of `127.0.0.1:5435`.)

   *(Optional)* Open `backend/.env` in your text editor and add your API keys:
   * `GROQ_API_KEY`: For ultra-fast streaming (Tier 1).
   * `GEMINI_API_KEY` / `OPENROUTER_API_KEY`: Secondary cloud LLM tiers.
   * `TAVILY_API_KEY`: For official SAP Help Portal web fallback & diagrams.
   > **Note**: Even without external API keys, Clyptus.AI automatically runs with its built-in local grounded synthesis engine!

---

### Step 4: Set Up Frontend

Open a new terminal window or tab:

```bash
cd frontend
npm install
```

---

### Step 5: Run the Application

You will run the backend and frontend in two separate terminal windows:

#### Terminal 1: Backend Server (FastAPI)
From the repository root (`SAP_BRIM_Ai`):
```bash
# Database first (no-op if it is already running)
docker compose up -d postgres

# Ensure your virtual environment is active (.venv)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
`/health` reports `"database": {"engine": "postgresql+pgvector", "status": "connected"}` and the document/chunk counts. If PostgreSQL goes down while the backend is running, API calls return `503 Database unavailable` instead of falling back to another store.
* **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### Terminal 2: Frontend Web Client (React 19 + Vite)
From the `frontend` folder:
```bash
cd frontend
npm run dev
```
* **Frontend Web App**: [http://localhost:5173](http://localhost:5173)

---

## 🔐 Credentials & Role-Based Access

The database automatically seeds an initial Super Admin account on startup:

| Portal | URL | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- | :--- |
| **Admin Control Center** | [http://localhost:5173/admin/login](http://localhost:5173/admin/login) | `vamshiyadav245@gmail.com` | `Vamshi@06` | Full Document Management, Ingestion Pipeline, Internal Sources Repository, Chunk Sandbox, System Security |
| **Standard User Chat** | [http://localhost:5173/app](http://localhost:5173/app) | *Any registered user* | *User password* | Enterprise Chat, Document Attachment Analysis, Recommended Follow-ups *(Sources and internal retrieval details strictly hidden)* |

> [!NOTE]
> Regular users can register freely at `/login?mode=register` or use the guest preview. Regular users **never see internal citations, document paths, or retrieval mechanics** — they receive clean, authoritative guidance.

---

## ⚡ Core Features & Capabilities

### 1. Real-Time Progressive Streaming (ChatGPT-Style)
* **Live Token-by-Token SSE Stream**: Answers stream progressively line-by-line as generated.
* **Animated Typing Indicator**: Displays a clean `"Thinking..."` state with animated dots while preparing retrieval.
* **Blinking Terminal Cursor**: Follows active generation in real time with auto-scrolling.
* **Follow-up Recommendations**: Generates exactly 3 clickable follow-up questions tailored to the response.

### 2. Enterprise Document Attachment & Extraction
* Upload PDF, DOCX, or text files directly in the chat input.
* Automatic text extraction, page parsing, and dedicated RAG grounding against uploaded files.

### 3. Role-Based Admin Control Center (`/admin`)
* **Document Manager**: Upload, view, re-index, or remove enterprise documentation with real-time status badges (Indexed, Processing, Vectorized).
* **Internal Sources Repository**: Search and inspect indexed technical source files and page counts.
* **Retrieval & Chunk Sandbox**: Test queries against the vector database, view top-k semantic matches, inspect similarity scores, and review reranking breakdowns.
* **Security & IP Protection**: Enforces backend token authentication (403 Forbidden on admin APIs for non-admins) and strips internal citations from regular user responses.

### 4. Multi-Tier Grounded RAG Pipeline
* **Tier 1 (Dense Search)**: 384-dimensional dense vectors generated by `sentence-transformers/all-MiniLM-L6-v2`.
* **Tier 2 (Lexical Search)**: BM25 keyword matching for exact SAP transaction codes, tables (`DFKKKO`, `FKKVKP`), and BAPIs.
* **Tier 3 (Cross-Encoder Reranking)**: `cross-encoder/ms-marco-MiniLM-L-6-v2` calibrates final relevance scores.
* **Tier 4 (Tavily SAP Web Fallback)**: Automatically queries authoritative `help.sap.com` documentation when internal confidence is weak.

### 5. Adaptive Answer Formatting
* Each answer is laid out to fit the question: a direct answer, a technical explanation, a comparison, step-by-step instructions, troubleshooting, or document research.
* Tables appear only for comparisons, genuinely tabular data, or when the user asks for one. Explicit requests such as "in a table", "without a table", "briefly" or "step by step" are followed.
* Grounding, claim verification and citations work exactly as before; only the layout changes.

---

## 📝 Recent Changes (2026-10-21)

### Chat experience
| Change | What it does | Main files |
|---|---|---|
| Removed "Relevant images" | Answers no longer show a web-image gallery, and the backend no longer calls Tavily for images. The `images` field stays in responses (always empty) so nothing that reads it breaks. | `ChatMessage.tsx`, `rag_service.py` |
| Chat-app layout | Your questions appear on the right in a bubble; answers stay on the left. | `ChatMessage.tsx` |
| Copy / Share / Edit under each question | **Copy** copies the question. **Edit** rewrites it: the old answer and every later message are deleted and a new answer is streamed. Files attached to the original question stay attached. | `ChatMessage.tsx`, `ChatPage.tsx`, `messages.py` |
| Share prompt dialog | **Share** opens a dialog with a preview and Copy link / X / LinkedIn / Reddit. The link (`/share/<token>`) opens a public page showing only the question text (never the answer, files or file names) with an "Ask Clyptus.AI this question" button that pre-fills the chat input. | `SharePromptModal.tsx`, `SharedPromptPage.tsx`, `shared.py`, `shared_prompt.py` |

### Answer Style Router
Answers used to come back as large Markdown tables with repeated sections. The cause was the prompts: the system prompt asked for "structured tables", and every question type was forced into a fixed 4–7 section template.

* **`answer_style_router.py`** (new) builds an internal answer plan once per question: `answer_type`, `detail_level`, `needs_table`, `needs_steps`, `needs_citations`, `source_mode` (internal / web / hybrid) and `max_sections`.
* **Rules first**, building on the existing `answer_planner` categories. Only questions the rules cannot place get one small, cached LLM classification, validated with Pydantic. Any failure falls back to a balanced technical explanation.
* **Prompts**: the rigid section templates are replaced by a short format directive plus formatting rules (answer first, no tables by default, state each fact once, no recap sections, cite only real `[E#]` IDs). The upgrade/reconciliation and block/restriction templates are kept because they carry safety content.
* **Pipeline**: the plan is routed once and reused for streaming, the fallback answer and repair. It is recorded only in the admin-only `validation_audit` and never streamed to users. SSE events are unchanged.
* **Fix**: `answer_planner` matched error words as substrings, so "issued" or "prefix" were treated as troubleshooting. It now matches whole words.

Live example ("How does SAP Convergent Invoicing aggregate billable items?"): before, 3,063 characters with a 7-row table holding paragraphs; after, about 1,100 characters with a direct answer and three cited bullets.

New settings (all optional; defaults shown):

| Setting | Default | Purpose |
|---|---|---|
| `ANSWER_STYLE_ROUTER_ENABLED` | `True` | `False` restores the previous template prompts |
| `ANSWER_STYLE_LLM_CLASSIFIER_ENABLED` | `True` | LLM classification for questions the rules cannot place |
| `ANSWER_STYLE_CLASSIFIER_MODEL` | `openai/gpt-oss-20b` | Groq model used for that classification |
| `ANSWER_STYLE_CLASSIFIER_TIMEOUT` | `4.0` | Seconds before falling back |
| `ANSWER_STYLE_DEFAULT` | `technical_explanation` | Style used when classification fails |
| `ANSWER_STYLE_DEFAULT_DETAIL` | `balanced` | `concise`, `balanced` or `detailed` |
| `ANSWER_STYLE_MAX_SECTIONS` | `4` | Heading budget for balanced answers |

### Backend API additions
| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/chats/{chat_id}/messages/{message_id}/edit` | Owner | Replace a question, delete later messages, stream a new answer (SSE) |
| `POST /api/chats/{chat_id}/messages/{message_id}/share` | Owner | Create or refresh the public link for a question; returns `{token}` |
| `GET /api/shared/prompts/{token}` | Public | Read a shared question |

The answer stream now also starts with a `{"type": "user_message", "message_id": ...}` event so the page knows the saved ID of the question being answered.

**Database:** a new `shared_prompts` table is created automatically when the backend starts. Restart the backend after pulling these changes.

### Known limitations
* Formatting is guided by the prompt; the model can still occasionally add a table or a recap.
* Logged-out visitors who click "Ask Clyptus.AI" on a shared link go through login and lose the pre-filled question.
* Share links use the current host (`localhost` in development), so they only work for others once the app is deployed.
* The older sidebar "Share chat" option builds a link that nothing handles yet.

---

## 🧪 Running Automated Tests

Tests never touch the live database: `backend/tests/conftest.py` redirects them to `<database>_test` (`sap_brim_ai_test`) and refuses to run against any database whose name does not end in `_test`. Create it once as a clone of the live database (it also gives retrieval tests the real knowledge base); drop and re-create it to reset:

```bash
docker exec sap_assistant_postgres createdb -U sap_assistant -O sap_brim_ai -T sap_brim_ai sap_brim_ai_test
```

Run the backend test suite to verify system integrity:

```bash
# Run all offline tests (tests marked "live" call external LLM/web APIs)
python -m pytest backend/tests -m "not live" -v

# PostgreSQL migration regression tests (no-fallback, 503 handling, exact vectors, retrieval parity)
python -m pytest backend/tests/test_postgres_migration.py -v

# Run admin security and role-enforcement tests
python -m pytest backend/tests/test_admin_portal_security.py -v

# Run live streaming and source hiding verification
python -m pytest backend/tests/test_streaming_and_source_hiding.py -v

# Answer Style Router (offline; LLM and retrieval mocked)
python -m pytest backend/tests/test_answer_style_router.py -v

# Edit and share prompt endpoints
python -m pytest backend/tests/test_edit_prompt.py backend/tests/test_share_prompt.py -v
```

---

## 📦 Project Structure

```text
SAP_BRIM_Ai/
├── README.md                           # Master setup and architecture documentation
├── docker-compose.yml                  # PostgreSQL + pgvector container (the only database)
├── .env.example                        # Compose settings template (ports, DB passwords)
├── docker/postgres/init/               # First-start script: sap_brim_ai role, database, vector extension
├── pytest.ini                          # Pytest configuration
│
├── backend/                            # FastAPI Backend Service
│   ├── .env.example                    # Environment variable template (DATABASE_URL, API keys)
│   ├── requirements.txt                # Python dependencies
│   ├── scripts/migrate_sqlite_to_pgvector.py  # One-time SQLite cutover utility (backup/migrate/verify)
│   │
│   ├── app/                            # Application Core
│   │   ├── main.py                     # FastAPI entrypoint and route mounting
│   │   ├── config.py                   # Pydantic application settings & feature flags
│   │   ├── database.py                 # PostgreSQL engine, schema/index setup, auto-seeding
│   │   ├── api/                        # API routes (auth, chats, messages, documents, rag_inspect)
│   │   ├── models/                     # SQLAlchemy models (User, Chat, Message, Document, Chunk)
│   │   ├── schemas/                    # Pydantic validation schemas
│   │   ├── security/                   # JWT authentication, password hashing, role guards
│   │   ├── services/                   # RAG service, LLM streaming failover, document extractor
│   │   └── retrieval/                  # Multi-source comparator, BM25 + dense search
│   │
│   └── tests/                          # Automated Pytest test suite
│
├── frontend/                           # React 19 + TypeScript + Vite Web Client
│   ├── package.json                    # Frontend dependencies
│   ├── vite.config.ts                  # Vite build and proxy config
│   ├── tailwind.config.js              # Tailwind styling
│   │
│   └── src/                            # Application Source Code
│       ├── main.tsx                    # React client entrypoint
│       ├── App.tsx                     # Application router and layout
│       ├── components/                 # Reusable UI components (chat, markdown, badges)
│       ├── context/                    # AuthContext and state providers
│       ├── layouts/                    # AppLayout, AdminProtectedRoute
│       ├── pages/                      # Page views (ChatPage, LandingPage, AdminDashboard, AdminLoginPage)
│       └── services/                   # SSE streaming client and REST API service calls
│
└── knowledge_base/                     # Canonical SAP BRIM PDF documents repository
    └── documents/                      # Pre-indexed courseware, guides, and SAP Press books
```

---

## 🛠️ Troubleshooting & FAQs

### 1. `Port 8000 or 5173 already in use`
* **Windows**: Open Task Manager or run:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  ```
* **macOS/Linux**:
  ```bash
  lsof -ti :8000 | xargs kill -9
  ```

### 2. Backend exits with `DATABASE UNAVAILABLE` / `Cannot connect to PostgreSQL`
1. Start the database: `docker compose up -d postgres`, then check `docker ps` shows `sap_assistant_postgres` as `healthy`.
2. Check `DATABASE_URL` in `backend/.env`: host port must match `POSTGRES_HOST_PORT` (default `5435`) and the password must match `SAP_BRIM_DB_PASSWORD`.
3. Port `5434` on this machine belongs to an unrelated container (`clyptus-postgres`); do not point the app at it.

### 3. Frontend fails to connect to backend
Ensure the backend server is running on `http://127.0.0.1:8000`. The Vite development server automatically proxies `/api/*` requests to port `8000`.

---

## 🗄️ Database: PostgreSQL + pgvector

| Setting | Value |
| :--- | :--- |
| Container / image | `sap_assistant_postgres` / `pgvector/pgvector:pg16` (pgvector 0.8.7) |
| Volume | `sap_projects_pgdata` (shared with SAP_Projects) |
| Host port | `127.0.0.1:5435` → container `5432` |
| Application database / role | `sap_brim_ai` / `sap_brim_ai` |
| Test database | `sap_brim_ai_test` (clone; used only by pytest) |
| Vector column | `document_chunks.embedding vector(384)` + HNSW index (`vector_cosine_ops`) + GIN full-text index |

**Backup and restore** (custom-format dump; run from the repository root):

```bash
docker exec sap_assistant_postgres pg_dump -U sap_assistant -d sap_brim_ai -Fc -f /tmp/sap_brim_ai.dump
docker cp sap_assistant_postgres:/tmp/sap_brim_ai.dump backups/postgres/

# Restore into an empty sap_brim_ai database (e.g. on another laptop after `docker compose up -d postgres`):
docker cp backups/postgres/sap_brim_ai.dump sap_assistant_postgres:/tmp/sap_brim_ai.dump
docker exec sap_assistant_postgres pg_restore -U sap_assistant -d sap_brim_ai --no-owner --role=sap_brim_ai /tmp/sap_brim_ai.dump
```

### Migration from SQLite (2026-10-16)

The knowledge base previously lived in `backend/sap_assistant.db` (SQLite). It was migrated with `backend/scripts/migrate_sqlite_to_pgvector.py`, which:
1. took a consistent backup and manifest (`backups/sqlite/`),
2. copied all 11 tables in one transaction with `ON CONFLICT (id) DO NOTHING` duplicate protection, transferring the existing embeddings verbatim (no re-embedding, re-chunking or re-ingestion),
3. verified every row and column, and every vector component for exact float32 equality, plus foreign keys and delete cascade.

The original `backend/sap_assistant.db` and its backup are kept until their deletion is explicitly authorised. Logs and reports are in `backups/migration_logs/`.

**Rollback to SQLite** (restores the pre-cutover code; other work in progress is untouched):
1. Stop the backend.
2. Reverse exactly the cutover changes: `git apply -R backups/cutover/postgres_cutover.patch`
3. If `backend/sap_assistant.db` is missing or altered, restore it from the backup and check its SHA-256 against `backups/sqlite/sap_assistant_20261016T054133Z.manifest.json`:
   `Copy-Item backups/sqlite/sap_assistant_20261016T054133Z.db backend/sap_assistant.db; attrib -R backend/sap_assistant.db`
4. Set `DATABASE_URL=postgresql://nobody@127.0.0.1:1/none` in `backend/.env`. The old code uses SQLite only when PostgreSQL is unreachable, and its built-in default (`localhost:5434`) points at an unrelated container on this machine.
5. Start the backend. The PostgreSQL `sap_brim_ai` database is left intact for a later re-cutover. Data written to PostgreSQL after the cutover is not copied back to SQLite.

---

## 📄 License
Proprietary & Confidential. All rights reserved by **Clyptus-Soft**.


How it works now
One plan per question. A new router, answer_style_router.py, decides the layout once, after evidence is selected. The same plan is used for the streamed answer, the fallback answer and any repair. It picks one of the six styles you specified (direct answer, explanation, comparison, steps, troubleshooting, document research), a detail level, whether a table or numbered steps fit, and a maximum number of headings.
Rules first. It builds on the planner's existing question categories, plus checks for explicit requests ("in a table", "without a table", "briefly", "step by step", bullets), how-to vs how-does wording, comparisons, error reports, document questions and short factual questions.
LLM only for unclear questions. Questions the rules can't place get one small, fast call to the Groq model openai/gpt-oss-20b. The result is checked against a strict schema and cached. If the call fails or returns anything invalid, the answer uses a balanced explanation.
Prompts. For most question types, a short format instruction replaces the rigid section templates, together with the formatting rules from your spec. Upgrade/reconciliation and business-partner block questions keep their structured templates, because those carry safety content.
Grounding is unchanged. Claim verification, repair, the safety guard and citation rules run exactly as before. When both internal documents and web results are used, the model is told to say which statements come from the web.
The plan stays internal. It is stored only in the admin-only audit data and is never streamed, so the SSE events are unchanged.
Frontend: headings now have sizes, h4 is styled, and table cells are top-aligned. Lists, code and table scrolling already rendered correctly.
Example answers (live runs against your dev database, web search off)
Before (router off): a 5-row table with whole paragraphs inside the cells. It explained aggregation twice, then added separate "Component" and "Release" blocks.
After: one direct sentence, three workflow bullets citing [E1]–[E5], and a one-line note on what the evidence doesn't cover.
Comparison (CI vs FI-CA): a one-sentence summary of the difference, a 3-row table with short cells, the key differences, and a conclusion.
Troubleshooting (billable items stuck in raw status): the cause labelled "Suspected", 7 numbered diagnostic steps, the fix, and verification steps.
The early live runs showed two leftovers, and I've fixed both in the prompts:

Recap sections: answers ended with "Key points" sections that repeated earlier content.
Invalid citation markers: the model wrote markers like [All evidence] and [E1-E5], which aren't real evidence IDs and aren't stripped for regular users.
Tests
New tests: I added test_answer_style_router.py with 31 offline tests, all passing. They cover your 14 cases plus caching, the planner fix and turning the router off. Case 11 runs the real streaming pipeline with retrieval and the LLM mocked.
Full backend suite: 239 passed and 8 failed. The 8 are the same ones that were already failing (6 document-dashboard tests plus test_integration_real_retriever_and_chunk_uuids and test_file_filtering_skips_binaries_and_lockfiles).
Frontend: the type check and build pass.
Configuration
Seven new settings in config.py, all with working defaults, so .env changes are optional:

Setting	Default
ANSWER_STYLE_ROUTER_ENABLED	True (set False to go back to the old template prompts)
ANSWER_STYLE_LLM_CLASSIFIER_ENABLED	True
ANSWER_STYLE_CLASSIFIER_MODEL	openai/gpt-oss-20b
ANSWER_STYLE_CLASSIFIER_TIMEOUT	4.0 seconds
ANSWER_STYLE_DEFAULT	technical_explanation
ANSWER_STYLE_DEFAULT_DETAIL	balanced
ANSWER_STYLE_MAX_SECTIONS	4
Limitations
Prompt guidance only. The model can still occasionally add a table or a recap. I didn't add an automatic rewrite step afterwards, because it could drop citations.
Most tests check prompts and routing, not live answers. The live runs above are the only check of actual output.
Other tests may hit the classifier live. Some existing pipeline tests call the real LLM, so an ambiguous question in them may trigger one classifier call.
A transaction question was refused. "What is transaction FKKBIXBIT_MON used for?" was turned down by the existing SAP topic check before reaching the router. That's unrelated to this change.
Other edits: I widened three test fakes in test_bp_block_regression.py to accept the new argument, and fixed the planner's error-word matching.
