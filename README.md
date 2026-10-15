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
* **Git**: [Download Git](https://git-scm.com/)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Clyptus-Soft/SAP_BRIM_Ai.git
cd SAP_BRIM_Ai
```

---

### Step 2: Set Up Backend

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

   *(Optional)* Open `backend/.env` in your text editor and add your API keys:
   * `GROQ_API_KEY`: For ultra-fast streaming (Tier 1).
   * `GEMINI_API_KEY` / `OPENROUTER_API_KEY`: Secondary cloud LLM tiers.
   * `TAVILY_API_KEY`: For official SAP Help Portal web fallback & diagrams.
   > **Note**: Even without external API keys, Clyptus.AI automatically runs with its built-in local grounded synthesis engine!

---

### Step 3: Set Up Frontend

Open a new terminal window or tab:

```bash
cd frontend
npm install
```

---

### Step 4: Run the Application

You will run the backend and frontend in two separate terminal windows:

#### Terminal 1: Backend Server (FastAPI)
From the repository root (`SAP_BRIM_Ai`):
```bash
# Ensure your virtual environment is active (.venv)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
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
* **Tier 5 (Visual Diagrams)**: Automatically fetches relevant SAP technical architecture diagrams and flowcharts for visual inquiries.

---

## 🧪 Running Automated Tests

Run the backend test suite to verify system integrity:

```bash
# Run all tests
python -m pytest backend/tests -v

# Run admin security and role-enforcement tests
python -m pytest backend/tests/test_admin_portal_security.py -v

# Run live streaming and source hiding verification
python -m pytest backend/tests/test_streaming_and_source_hiding.py -v
```

---

## 📦 Project Structure

```text
SAP_BRIM_Ai/
├── README.md                           # Master setup and architecture documentation
├── docker-compose.yml                  # Optional PostgreSQL + pgvector container definition
├── pytest.ini                          # Pytest configuration
│
├── backend/                            # FastAPI Backend Service
│   ├── .env.example                    # Environment variable template
│   ├── requirements.txt                # Python dependencies
│   ├── sap_assistant.db                # Pre-indexed SQLite database
│   │
│   ├── app/                            # Application Core
│   │   ├── main.py                     # FastAPI entrypoint and route mounting
│   │   ├── config.py                   # Pydantic application settings & feature flags
│   │   ├── database.py                 # SQLAlchemy engine, migrations, auto-seeding
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

### 2. How to run with PostgreSQL instead of SQLite?
1. Start the Docker container:
   ```bash
   docker-compose up -d
   ```
2. Update `DATABASE_URL` in `backend/.env`:
   ```ini
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sap_assistant
   ```

### 3. Frontend fails to connect to backend
Ensure the backend server is running on `http://127.0.0.1:8000`. The Vite development server automatically proxies `/api/*` requests to port `8000`.

---

## 📄 License
Proprietary & Confidential. All rights reserved by **Clyptus-Soft**.
