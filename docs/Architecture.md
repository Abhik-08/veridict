# Veridict Architecture Overview

Veridict is an enterprise-grade AI response quality evaluation system built on a **Multi-Agent Evaluation Pipeline** combined with **Retrieval-Augmented Generation (RAG)**.

---

## High-Level System Architecture

```
                       +-------------------+
                       |   React Frontend  |
                       | (Vite + Tailwind) |
                       +---------+---------+
                                 |
                                 | HTTP / REST
                                 v
                       +-------------------+
                       |  FastAPI Backend  |
                       +---------+---------+
                                 |
         +-----------------------+-----------------------+
         |                       |                       |
         v                       v                       v
+-----------------+    +-------------------+    +------------------+
| Semantic RAG    |    | Multi-Agent       |    | Report Generator |
| Retrieval Engine|    | Evaluation Engine |    | (ReportLab PDF)  |
+--------+--------+    +---------+---------+    +------------------+
         |                       |
         v                       v
+-----------------+    +-------------------+
| Pinecone Vector |    |  JudgeLLMService  |
| Database        |    | (Fallback Chain)  |
+-----------------+    +---------+---------+
                                 |
                                 v
                       +-------------------+
                       | Gemini AI Models  |
                       | (2.5, 3.1, 3.5)   |
                       +-------------------+
```

---

## Core Architectural Components

### 1. Multi-Agent Evaluation Engine
Veridict employs four specialized judge agents operating independently, followed by a Verdict Agent that aggregates scores into a final verdict:

- **Relevance Judge**: Evaluates topical alignment between the prompt and the generated AI response (1–5 score).
- **Accuracy Judge**: Verifies factual correctness against ground-truth reference answers and retrieved evidence (1–5 score).
- **Completeness Judge**: Assesses whether all critical concepts and nuances from reference material are addressed (1–5 score).
- **Hallucination Judge**: Detects ungrounded or fabricated claims by comparing the response strictly against retrieved context (1–5 score).
- **Verdict Agent**: Computes a weighted overall evaluation score (1.00–5.00) and assigns an actionable verdict status:
  - **PASS** (Score $\ge 4.0$)
  - **NEEDS IMPROVEMENT** ($3.0 \le \text{Score} < 4.0$)
  - **FAIL** ($\text{Score} < 3.0$)

---

### 2. Resilient Judge LLM Infrastructure (`JudgeLLMService`)
To guarantee high availability and rate-limit resilience during evaluations, Veridict implements an automated model fallback chain:

1. **Primary Model**: `gemini-2.5-flash`
2. **First Fallback**: `gemini-3.1-flash-lite`
3. **Second Fallback**: `gemini-3.5-flash`

#### Key Features:
- **Exponential Backoff**: Automatic retry handling for transient API errors or HTTP 429 rate limits.
- **Structured JSON Validation**: Enforces strict Pydantic schema validation on raw LLM outputs.
- **Model Usage Tracking**: Records which specific LLM model completed each evaluation dimension.

---

### 3. RAG Retrieval & Ingestion Engine
- **Knowledge Base Ingestion**: Processes benchmark datasets (SQuAD, TruthfulQA) into semantic chunks embedded using Google `gemini-embedding-001`.
- **Vector Search**: Queries Pinecone vector index (`veridict-knowledge-base`) for top-K semantically relevant evidence chunks.
- **PDF Upload Context**: Supports dynamic, temporary PDF namespace ingestion with background processing and hourly TTL cleanup.

---

### 4. Batch Evaluation Engine
- **Decoupled Architecture**: Operates independently from Single Evaluation to prevent pipeline interference.
- **Abstract Parser & Exporter Factories**: Supports CSV and Digital QA PDF parsing via extensible strategy interfaces.
- **Rate Controller & Concurrency**: Manages inter-batch throttling delays and asynchronous background job state.
