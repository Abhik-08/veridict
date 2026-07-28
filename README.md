# Veridict — AI Response Quality Evaluator Agent

An AI-powered platform for evaluating the quality of AI-generated responses using Retrieval-Augmented Generation (RAG) and a Multi-Agent Judging Pipeline.

Veridict analyzes AI responses across four quality dimensions — **Relevance**, **Accuracy**, **Completeness**, and **Hallucination** — providing transparent scoring, confidence metrics, explainable reasoning, and executive PDF reports.

<img width="575" height="775" alt="Veridict Dashboard" src="https://github.com/user-attachments/assets/44edbbd3-207a-4989-af83-080832a02de7" />

---

## Why Veridict?

Large Language Models (LLMs) frequently generate answers that appear fluent and convincing yet suffer from factual errors, omissions, or ungrounded hallucinations. **Veridict** provides an objective, automated framework to evaluate AI outputs against ground-truth benchmarks and uploaded reference documents.

Designed for developers, researchers, and enterprise AI teams, Veridict delivers transparent quality assessment through both interactive single-response evaluations and bulk dataset evaluation pipelines.

---

## Key Features

- 🤖 **Multi-Agent Judging Engine**: Independent evaluation agents score Relevance, Accuracy, Completeness, and Hallucination.
- ⚖️ **Weighted Verdict Agent**: Computes aggregated scores (1.00–5.00) and assigns an actionable verdict (**PASS**, **NEEDS IMPROVEMENT**, or **FAIL**).
- ⚡ **Single & Batch Evaluation Modes**: Evaluate individual QA pairs or upload dataset CSVs / Digital QA PDFs for bulk assessment.
- 📚 **RAG-Powered Grounding**: Semantic retrieval against Pinecone vector search index and user-uploaded reference PDFs.
- 🛡️ **Resilient LLM Infrastructure**: Automated multi-model fallback chain (`gemini-2.5-flash` → `gemini-3.1-flash-lite` → `gemini-3.5-flash`) with rate-limit retry handling.
- 📄 **Executive PDF Reports**: Stream structured multi-page PDF evaluation assessment reports for archiving and presentation.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, TypeScript 6, Tailwind CSS 4, Lucide React, Axios |
| **Backend** | FastAPI (Python 3.12), Pydantic v2, Google GenAI SDK, Pinecone SDK, ReportLab, PyPDF, Pandas |
| **AI / Vector Store** | Google Gemini (2.5 Flash / 3.1 Flash Lite / 3.5 Flash), Google Embedding (001), Pinecone Vector Database |

---

## Architecture Overview

```
User (Browser)
     │
     ▼
React Frontend (Single & Batch Dashboards)
     │
     ▼
FastAPI Backend API
     ├── RAG Retrieval Engine (Pinecone Vector DB)
     ├── PDF Ingestion Service (Async Background Worker)
     ├── Multi-Agent Evaluation Engine (Relevance, Accuracy, Completeness, Hallucination)
     ├── Verdict Agent (Weighted Scoring & Verdict Assignment)
     └── Report Generator (Executive PDF & CSV Exports)
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
Add your `GOOGLE_API_KEY` and `PINECONE_API_KEY` to `backend/.env`.

Start the backend server:
```bash
python -m uvicorn app.main:app --port 8000
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
# Backend test suite (123 tests)
cd ../backend
python -m pytest tests/ -v
```

---

## Configuration

Environment variables are managed in `backend/.env`. Refer to [`.env.example`](backend/.env.example`) for default settings and available configuration parameters.

---

## Documentation Index

Explore the `docs/` directory for detailed technical guides:

- 📐 **[Architecture Overview](docs/Architecture.md)** — Multi-agent pipeline, model fallback chain, and scoring formulas.
- 🔌 **[REST API Reference](docs/API.md)** — Complete API endpoints, request schemas, and payload examples.
- 📊 **[Batch Evaluation Guide](docs/Batch_Evaluation.md)** — CSV/PDF bulk processing, parsers, and progress tracking.
- 🔍 **[RAG Pipeline Details](docs/RAG_Pipeline.md)** — Document chunking, embeddings, and Pinecone vector search.
- 🛠️ **[Development Guide](docs/Development.md)** — Local setup, testing guidelines, and project organization.

---

## Author

**Abhik Mukherjee**  
B.Tech Computer Science & Engineering | Dr. B. C. Roy Engineering College  
AI Intern — Infosys Springboard Virtual Internship (Batch 1)  

---

## License

This project is licensed under the [MIT License](LICENSE).
