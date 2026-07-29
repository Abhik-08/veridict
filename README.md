# Veridict — Enterprise AI Response Quality & Hallucination Evaluator

An enterprise-grade, full-stack platform for evaluating the quality, accuracy, and hallucination risk of AI-generated responses using Retrieval-Augmented Generation (RAG), a Multi-Agent Judging Pipeline, and automated Supabase PostgreSQL history persistence.

Veridict evaluates AI outputs across four core dimensions — **Relevance**, **Accuracy**, **Completeness**, and **Hallucination** — providing weighted overall scoring (1.00–5.00), confidence metrics, explainable reasoning, executive PDF exports, searchable evaluation history, and interactive analytics.

<img width="575" height="775" alt="Veridict Dashboard" src="https://github.com/user-attachments/assets/44edbbd3-207a-4989-af83-080832a02de7" />

---

## Why Veridict?

Large Language Models (LLMs) frequently generate answers that appear fluent and convincing yet suffer from factual errors, omissions, or ungrounded hallucinations. **Veridict** provides an objective, automated framework to evaluate AI outputs against ground-truth benchmarks and uploaded reference documents.

Designed for developers, researchers, and enterprise AI teams, Veridict delivers transparent quality assessment through interactive single-prompt evaluations, bulk dataset evaluation pipelines, searchable history auditing, and KPI analytics.

---

## Key Features

- 🤖 **Multi-Agent Judging Engine**: Independent evaluation agents score Relevance, Accuracy, Completeness, and Hallucination.
- ⚖️ **Weighted Verdict Agent**: Computes aggregated overall scores (1.00–5.00) and assigns an actionable verdict (**PASS**, **NEEDS IMPROVEMENT**, or **FAIL**).
- ⚡ **Single & Batch Evaluation Modes**: Evaluate individual QA pairs or upload dataset CSVs / Digital QA PDFs for bulk assessment.
- 📚 **RAG-Powered Grounding**: Semantic retrieval against Pinecone vector search index and user-uploaded reference PDFs.
- 🛡️ **Resilient LLM Infrastructure**: Automated multi-model fallback chain (`gemini-2.5-flash` → `gemini-3.1-flash-lite` → `gemini-3.5-flash`) with rate-limit retry handling.
- 🗄️ **Automatic PostgreSQL Persistence**: Automatically stores evaluation records, confidence metrics, RAG evidence, and multi-agent JSON payloads in Supabase PostgreSQL database.
- 📊 **Evaluation History & Dashboard**: Full history module with debounced search, multi-field filtering, sticky headers, stacked dates, active filter chips, KPI statistics, and manual multi-select bulk deletion.
- 📄 **Executive PDF Reports**: Stream structured multi-page PDF evaluation assessment reports for archiving and presentation.
- 🎨 **Modern Streamlined UI/UX**: Popup-free evaluation submission flow with inline step-by-step progress cards and auto-dismissing success notifications.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, TypeScript 6, Tailwind CSS 4, Lucide React, Axios, React Router 7 |
| **Backend** | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0, Alembic, Supabase SDK, ReportLab, PyPDF, Pandas |
| **AI & Vector Store** | Google Gemini (`2.5 Flash`, `3.1 Flash Lite`, `3.5 Flash`), Google Embedding (`001`), Pinecone Vector DB |
| **Database & Auth** | Supabase PostgreSQL, JWT Authentication, Row-Level Security, Alembic Migrations |

---

## Architecture Overview

```
User (Browser)
     │
     ▼
React 19 Frontend (Single & Batch Dashboards, History & KPI Overview)
     │
     ▼ REST APIs (Axios + JWT)
FastAPI Backend Application (`app/`)
     ├── Shared Common Infrastructure (`app.common`)
     ├── RAG Retrieval Engine (Pinecone Vector DB)
     ├── Multi-Agent Evaluation Engine (Relevance, Accuracy, Completeness, Hallucination)
     ├── Verdict Agent (Weighted Scoring & Verdict Assignment)
     ├── Repository & Service Persistence Layer (`app.history`)
     └── Supabase PostgreSQL Database (SQLAlchemy + Alembic)
     │
     ▼
Google Gemini LLM Chain (Primary + Fallback Models)
```

> 📖 For full system design details, see [Architecture Documentation](docs/Architecture.md).

---

## Quickstart

### Prerequisites
- **Python 3.12+**
- **Node.js 20+**
- **Google Gemini API Key**
- **Pinecone API Key**
- **Supabase PostgreSQL Database**

### 1. Clone Repository
```bash
git clone https://github.com/Abhik-08/veridict.git
cd veridict
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate Virtual Environment (Windows: .\venv\Scripts\activate | Unix: source venv/bin/activate)
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```
Add your `GOOGLE_API_KEY`, `PINECONE_API_KEY`, and `DATABASE_URL` to `backend/.env`.

Apply database migrations:
```bash
alembic stamp 001_initial_schema
alembic upgrade head
```

Start backend server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 4. Running Tests
```bash
# Backend test suite (151 tests passing cleanly)
cd ../backend
python -m pytest tests/ -v
```

---

## Documentation Index

Explore the `docs/` directory for detailed technical guides:

- 📐 **[Architecture Overview](docs/Architecture.md)** — Multi-agent pipeline, model fallback chain, shared common infrastructure, and repository pattern.
- 🔌 **[REST API Reference](docs/API.md)** — Complete REST endpoints for single evaluation, batch processing, authentication, and history auditing.
- 📊 **[Batch Evaluation Guide](docs/Batch_Evaluation.md)** — CSV/PDF bulk processing, parsers, and rate controllers.
- 🔍 **[RAG Pipeline Details](docs/RAG_Pipeline.md)** — Document chunking, embeddings, Pinecone vector search, and evidence binding.
- 🛠️ **[Development Guide](docs/Development.md)** — Local setup, database migrations, pytest guidelines, and project organization.

---

## Author

**Abhik Mukherjee**  
B.Tech Computer Science & Engineering | Dr. B. C. Roy Engineering College  
AI Intern — Infosys Springboard Virtual Internship (Batch 1)  

---

## License

This project is licensed under the [MIT License](LICENSE).
