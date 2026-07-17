# Veridict – AI Response Quality Evaluator Agent

An AI-powered platform for evaluating the quality of AI-generated responses using Retrieval-Augmented Generation (RAG) and a Multi-Agent Judging Pipeline.

Veridict analyzes AI responses across multiple quality dimensions (Relevance, Accuracy, and Hallucination), provides explainable reasoning, and displays a comprehensive evaluation verdict in a clean React interface.

<img width="575" height="775" alt="Screenshot" src="https://github.com/user-attachments/assets/44edbbd3-207a-4989-af83-080832a02de7" />

---

## Project Overview

Large Language Models (LLMs) often produce responses that may be relevant but factually incorrect, incomplete, or hallucinated. Veridict is designed to objectively evaluate AI-generated responses by combining semantic retrieval with specialized AI judge agents.

The platform assists developers, researchers, educators, and organizations in assessing the reliability and quality of AI outputs with transparent scoring and reasoning.

---

## Current Progress (Milestone 2 - Completed)

All core components of Milestone 1 and Milestone 2 have been fully implemented and verified:
- **Vite + React Frontend**: High-performance UI for submitting questions, AI responses, and uploading reference PDFs. Includes an expandable retrieved context section.
- **FastAPI Backend**: Asynchronous REST API managing evaluations, document ingestion, and task job states.
- **Optimized PDF Ingestion**: Asynchronous pipeline extracting text, dividing it into semantic paragraphs, computing batch embeddings, caching namespaces by file fingerprint (MD5), and upserting vectors to Pinecone.
- **Pinecone Vector Database**: Semantic search querying, filtering by temporary namespace, and RAG retrieval.
- **JudgeLLMService**: Resilient structured LLM model fallback chain (`gemini-2.5-flash` -> `gemini-3.1-flash-lite` -> `gemini-3.5-flash`) with exponential backoffs, JSON output parsing, and error recovery.
- **Multi-Agent Evaluation**: Three specialized evaluation agents:
  - **Relevance Judge**: Scores prompt-to-response topical relevance (1-5).
  - **Accuracy Judge**: Scores factual correctness against reference answers and retrieved evidence (1-5).
  - **Hallucination Judge**: Scores factual grounding against retrieved evidence (1-5).

---

## System Architecture

```
User
    │
    ▼
React Frontend
    │
    ▼
FastAPI Backend
    ├── Evaluation Endpoint (/evaluate)
    ├── PDF Ingestion Service (Async / Background)
    ├── Reference Knowledge Base & RAG Retrieval
    ├── JudgeLLMService (Resilient model fallback chain)
    └── Specialized Judge Agents (Relevance, Accuracy, Hallucination)
    │
    ▼
External AI Services
    ├── Gemini API (Models: gemini-2.5-flash, gemini-3.1-flash-lite, gemini-3.5-flash)
    └── Google Embedding API (gemini-embedding-001)
    │
    ▼
Data Layer
    ├── Pinecone Vector Database (Index: veridict-knowledge-base)
    └── Local cache registry (pdf_cache.json, ingestion_jobs.json)
```

---

## Tech Stack

### Frontend
- **React** (v18)
- **Vite** (v6)
- **TypeScript** (v5)
- **Tailwind CSS** (v4)
- **Lucide React** (Icons)

### Backend
- **FastAPI** (Python v3.12)
- **Pydantic** (v2)
- **Google GenAI SDK** (`google-genai`)
- **Pinecone Client** (`pinecone`)
- **PyPDF** (PDF Parsing)
- **Uvicorn** (ASGI Server)

---

## Folder Structure

```
veridict/
├── backend/
│   ├── app/
│   │   ├── agents/         # Relevance, Accuracy, and Hallucination Judge Agents
│   │   ├── api/            # Router endpoints (/evaluate and /evaluate/status/{ns})
│   │   ├── core/           # Config settings and custom exception handling
│   │   ├── knowledge/      # Knowledge-base loaders, preprocessors, and builders
│   │   ├── schemas/        # Request/Response Pydantic schemas
│   │   └── services/       # Ingestion, caching, retrieval, and LLM judge services
│   ├── scripts/            # Script folder
│   │   └── dev/            # Relocated manual/E2E test scripts
│   ├── tests/              # Pytest backend test suite
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # UI cards, results layout, and spinners
│   │   ├── pages/          # Main HomePage interface
│   │   ├── services/       # Axios API client
│   │   └── types/          # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Getting Started

### Clone Repository
```bash
git clone https://github.com/Abhik-08/veridict.git
cd veridict
```

### Backend Setup
1. Navigate to backend:
   ```bash
   cd backend
   ```
2. Create virtual environment and install packages:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up environment variables inside `.env` (refer to `.env.example`):
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```
4. Start development server:
   ```bash
   python -m uvicorn app.main:app --port 8000
   ```

### Frontend Setup
1. Navigate to frontend:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start React server:
   ```bash
   npm run dev
   ```
4. Open the app in browser at `http://localhost:5173`.

### Running Tests
Inside active virtual environment in the `backend/` directory, run:
```bash
pytest tests/ -v
```

---

## Author

**Abhik Mukherjee**  
B.Tech Computer Science & Engineering  
Dr. B. C. Roy Engineering College  

AI Intern – Infosys Springboard Virtual Internship (Batch 1)  
Project: **Veridict – AI Response Quality Evaluator Agent**

---

## License
This project is developed as part of the Infosys Springboard Virtual Internship Program.
