# Veridict Architecture Overview

Veridict is an enterprise-grade AI response quality evaluation platform built on a **Multi-Agent Evaluation Engine**, **Retrieval-Augmented Generation (RAG)**, **Shared Common Infrastructure (`app.common`)**, **Repository-Service Pattern**, and **Supabase PostgreSQL Persistence**.

---

## High-Level System Architecture

```
                       +-------------------+
                       |   React Frontend  |
                       | (Vite + Tailwind) |
                       +---------+---------+
                                 |
                                 | REST APIs (Axios)
                                 v
                       +-------------------+
                       |  FastAPI Backend  |
                       +---------+---------+
                                 |
          +----------------------+----------------------+
          |                      |                      |
          v                      v                      v
+------------------+   +-------------------+  +-------------------+
|  Shared Common   |   | Multi-Agent       |  | History Engine    |
| Infrastructure   |   | Evaluation Engine |  | (Repo/Service)    |
| (`app.common`)   |   +---------+---------+  +---------+---------+
+------------------+             |                      |
                                 v                      v
                       +-------------------+  +-------------------+
                       |  JudgeLLMService  |  | Supabase Postgres |
                       | (Fallback Chain)  |  | Database          |
                       +---------+---------+  +-------------------+
                                 |
                                 v
                       +-------------------+
                       | Gemini AI Models  |
                       | (2.5, 3.1, 3.5)   |
                       +-------------------+
```

---

## Core Architectural Components

### 1. Shared Common Infrastructure (`app.common`)
Centralized framework-agnostic foundation package providing standardized primitives across all feature modules:
- **Constants**: `DEFAULT_PAGE`, `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE`, `DEFAULT_SORT_FIELD`, `DEFAULT_SORT_ORDER`.
- **Types**: `UUIDType`, `SortOrderEnum`, `PageNumber`, `PageSize`, `DateRange`, `ScoreRange`, `ConfidenceRange`.
- **Models**: `RequestMetadata`, `ResponseMetadata`, `PaginationMetadata`, `PaginatedResponse[T]`, `SuccessResponse[T]`, `ErrorResponse`.
- **Exceptions**: `BaseAppException`, `NotFoundException`, `UnauthorizedException`, `ForbiddenException`, `ValidationException`, `BusinessRuleException`.
- **Utils**: Reusable datetime helpers (`utcnow`), filter validators, pagination calculators, sorting sanitizers, and boundary input validators.

---

### 2. Multi-Agent Evaluation Engine
Four specialized judge agents operate independently, followed by a Verdict Agent that aggregates scores into a final verdict:
- **Relevance Judge**: Evaluates topical alignment between the prompt and the generated AI response (1.0–5.0 score).
- **Accuracy Judge**: Verifies factual correctness against ground-truth reference answers and retrieved evidence (1.0–5.0 score).
- **Completeness Judge**: Assesses whether all critical concepts and nuances from reference material are addressed (1.0–5.0 score).
- **Hallucination Judge**: Detects ungrounded or fabricated claims by comparing the response strictly against retrieved context (1.0–5.0 score).
- **Verdict Agent**: Computes a weighted overall evaluation score (1.00–5.00) and assigns an actionable verdict status:
  - **PASS** ($\text{Score} \ge 4.0$)
  - **NEEDS IMPROVEMENT** ($3.0 \le \text{Score} < 4.0$)
  - **FAIL** ($\text{Score} < 3.0$)

---

### 3. Automatic Persistence & History Architecture (`app.history`)
- **Transparent Persistence**: Evaluation calls (`/evaluate` and `/evaluate/batch`) automatically persist evaluation results, confidence scores, RAG evidence, and multi-agent JSON payloads via domain events (`EvaluationCreatedEvent`).
- **Repository Pattern**: `HistoryRepository` decouples raw database access queries from business logic.
- **Service Layer**: `HistoryService` handles filtering, pagination calculations, statistics aggregation, and user isolation scoping.
- **Mapper Layer**: `HistoryMapper` transforms raw evaluation models into clean DTO response schemas.

---

### 4. Resilient Judge LLM Infrastructure (`JudgeLLMService`)
To guarantee high availability and rate-limit resilience during evaluations, Veridict implements an automated model fallback chain:
1. **Primary Model**: `gemini-2.5-flash`
2. **First Fallback**: `gemini-3.1-flash-lite`
3. **Second Fallback**: `gemini-3.5-flash`

#### Key Features:
- **Exponential Backoff**: Automatic retry handling for transient API errors or HTTP 429 rate limits.
- **Structured JSON Validation**: Enforces strict Pydantic schema validation on raw LLM outputs.
- **Model Usage Tracking**: Records which specific LLM model completed each evaluation dimension.

---

### 5. RAG Retrieval & Ingestion Engine
- **Knowledge Base Ingestion**: Processes benchmark datasets (SQuAD, TruthfulQA) into semantic chunks embedded using Google `gemini-embedding-001`.
- **Vector Search**: Queries Pinecone vector index (`veridict-knowledge-base`) for top-K semantically relevant evidence chunks.
- **PDF Upload Context**: Supports dynamic, temporary PDF namespace ingestion with background processing and hourly TTL cleanup.

---

### 6. Frontend Presentation & UI/UX Architecture
- **State Management**: Custom React hooks (`useHistory`, `useDashboard`, `useEvaluation`, `useAuth`) separating UI presentation from state logic.
- **Micro-Interactions**: Smooth 150–200ms cubic-bezier transition curves on table rows, action buttons, filter chips, and card hover states.
- **Manual Multi-Select Bulk Delete**: Floating action bar allowing manual row selection and sequential item deletion via existing REST APIs.
- **Streamlined Popup-Free UX**: Direct inline loading card progress presentation and single auto-dismissing toast notifications.
