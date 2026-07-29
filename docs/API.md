# Veridict REST API Documentation

The Veridict backend is built using FastAPI and provides asynchronous, production-ready REST endpoints for Single Evaluation, Batch Evaluation, Evaluation History, PDF Report Generation, and Semantic Retrieval.

Base URL: `http://localhost:8000`

---

## 1. Authentication API (`/auth`)

### `POST /auth/login`
Authenticates user credentials and returns a JWT access token.

### `POST /auth/register`
Registers a new user account in Supabase PostgreSQL database.

### `GET /auth/me`
Returns current authenticated user profile context.

---

## 2. Single Evaluation API (`/evaluate`)

### `POST /evaluate`
Submits a question, AI response, optional reference answer, and optional reference PDF for multi-agent evaluation. Automatically persists results to Evaluation History.

#### Request (`multipart/form-data`)
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `question` | string | Yes | The prompt or question asked to the AI |
| `ai_response` | string | Yes | The generated AI response to evaluate |
| `reference_answer` | string | No | Ground-truth reference answer (optional) |
| `pdf_file` | file | No | PDF document for background RAG ingestion (optional) |

#### Response (`200 OK`)
```json
{
  "evaluation_id": "e204c397-b898-4d27-b389-73d6d1a57fcb",
  "question": "What is Retrieval-Augmented Generation?",
  "ai_response": "RAG combines search retrieval with generative models...",
  "verdict": "PASS",
  "overall_score": 4.85,
  "confidence": 0.95,
  "judges": {
    "relevance": { "score": 5.0, "confidence": 0.95, "reasoning": "Directly answers question." },
    "accuracy": { "score": 5.0, "confidence": 0.92, "reasoning": "Factually accurate." },
    "completeness": { "score": 4.0, "confidence": 0.88, "reasoning": "Covers primary concepts." },
    "hallucination": { "score": 5.0, "confidence": 0.96, "reasoning": "Grounded in retrieved text." }
  },
  "retrieved_evidence": [...]
}
```

### `POST /evaluate/export-pdf`
Generates and streams an executive PDF assessment report binary.

### `GET /evaluate/status/{namespace}`
Checks PDF ingestion job status and embedding performance metrics.

---

## 3. Batch Evaluation API (`/evaluate/batch`)

### `POST /evaluate/batch/csv`
Uploads a CSV file containing `Question` and `AI Response` columns for batch evaluation. Automatically persists batch job and item history.

### `POST /evaluate/batch/pdf`
Uploads a searchable Digital QA PDF for batch evaluation.

### `GET /evaluate/batch/progress/{batch_id}`
Returns real-time batch job progress, item status counts, and dimension averages.

### `GET /evaluate/batch/export-csv/{batch_id}`
Downloads completed batch evaluation results as a structured CSV file.

### `GET /evaluate/batch/export-pdf/{batch_id}`
Downloads executive batch summary as a multi-page PDF report.

---

## 4. Evaluation History API (`/history`)

All History endpoints enforce user isolation based on authenticated JWT credentials.

### `GET /history`
Returns paginated, searchable, and filtered evaluation history items.

#### Query Parameters
- `page` (int, default: 1): 1-based page number.
- `page_size` (int, default: 10, max: 100): Items per page.
- `search` (string, optional): Full-text search across question, response, reference, and reasoning.
- `verdict` (string, optional): Filter by `PASS`, `NEEDS_IMPROVEMENT`, or `FAIL`.
- `source_type` (string, optional): Filter by `SINGLE` or `BATCH`.
- `sort_by` (string, default: `created_at`): Sort field name.
- `sort_order` (string, default: `DESC`): Sort direction (`ASC` or `DESC`).
- `date_from` (ISO string, optional): Filter records created after date.
- `date_to` (ISO string, optional): Filter records created before date.
- `score_min` (float, optional): Minimum overall score.
- `score_max` (float, optional): Maximum overall score.

### `GET /history/stats`
Returns aggregated history KPIs: total evaluations, pass/fail/improvement counts, overall average score, average confidence, single vs batch counts.

### `GET /history/recent`
Returns top 10 most recent evaluation activity items.

### `GET /history/{id}`
Returns full evaluation inspection details including RAG evidence breakdown and multi-agent JSON payload.

### `DELETE /history/{id}`
Permanently deletes an evaluation record by ID.

### `GET /history/batches`
Returns paginated list of batch jobs.

### `GET /history/batches/{id}`
Returns batch job summary details and associated evaluation items.

### `DELETE /history/batches/{id}`
Deletes a batch job and cascades deletion of all associated evaluation items.

---

## 5. Semantic Retrieval API (`/retrieve`)

### `POST /retrieve`
Queries the Pinecone vector database for top-K semantically relevant knowledge chunks.

#### Request Body
```json
{
  "query": "Explain transformer self-attention mechanisms",
  "top_k": 5
}
```
