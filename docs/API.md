# Veridict REST API Documentation

The Veridict backend is built using FastAPI and provides asynchronous REST endpoints for Single Evaluation, Batch Evaluation, PDF Report Generation, and Semantic Retrieval.

Base URL: `http://localhost:8000`

---

## 1. Single Evaluation API

### `POST /evaluate`
Submits a question, AI response, optional reference answer, and optional reference PDF for multi-agent evaluation.

#### Request (Multipart Form Data)
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `question` | string | Yes | The prompt or question asked to the AI |
| `ai_response` | string | Yes | The generated AI response to evaluate |
| `reference_answer` | string | No | Ground-truth reference answer (optional) |
| `pdf_file` | file | No | PDF document for background ingestion (optional) |

#### Response (`200 OK`)
```json
{
  "evaluation_id": "eval_123456",
  "question": "What is Retrieval-Augmented Generation?",
  "ai_response": "RAG combines search retrieval with generative models...",
  "verdict": "PASS",
  "overall_score": 4.85,
  "judges": {
    "relevance": { "score": 5, "confidence": 0.95, "reasoning": "Directly answers question." },
    "accuracy": { "score": 5, "confidence": 0.92, "reasoning": "Factually accurate." },
    "completeness": { "score": 4, "confidence": 0.88, "reasoning": "Covers primary concepts." },
    "hallucination": { "score": 5, "confidence": 0.96, "reasoning": "Grounded in retrieved text." }
  },
  "retrieved_context": [...]
}
```

---

### `POST /evaluate/export-pdf`
Generates and streams an executive PDF assessment report.

#### Request Body (`application/json`)
Passes the complete evaluation result payload.

#### Response (`200 OK`)
Binary stream (`application/pdf`).

---

### `GET /evaluate/status/{namespace}`
Checks PDF ingestion job status and embedding performance metrics.

---

## 2. Batch Evaluation API

### `POST /evaluate/batch/csv`
Uploads a CSV file containing `Question` and `AI Response` columns for batch evaluation.

### `POST /evaluate/batch/pdf`
Uploads a searchable Digital QA PDF for batch evaluation.

### `GET /evaluate/batch/progress/{batch_id}`
Returns real-time progress, processed item counts, dimension averages, and job metadata.

### `GET /evaluate/batch/export-csv/{batch_id}`
Downloads completed batch evaluation results as a structured CSV file.

### `GET /evaluate/batch/export-pdf/{batch_id}`
Downloads executive batch summary as a multi-page PDF report.

---

## 3. Semantic Retrieval API

### `POST /retrieve`
Queries the Pinecone vector database for top-K semantically relevant knowledge chunks.

#### Request Body
```json
{
  "query": "Explain transformer self-attention mechanisms",
  "top_k": 5
}
```
