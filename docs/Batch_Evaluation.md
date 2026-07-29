# Veridict Batch Evaluation Module

The Batch Evaluation module enables bulk assessment of AI-generated responses across large datasets using CSV or Digital QA PDF uploads.

---

## Key Capabilities

- **CSV Dataset Ingestion**: Automatic parsing and normalization of dataset CSV files (`Question`, `AI Response`, `Reference Answer` columns).
- **Digital QA PDF Parsing**: Automated extraction of Question/Answer blocks from structured digital PDF documents.
- **Evidence Context Binding**: Optional binding of a reference PDF document to provide evidence for all batch rows.
- **Asynchronous Batch Execution**: Non-blocking background worker execution with progress reporting.
- **Rate Limit & Concurrency Control**: Automatic rate-limiting controller regulating inter-batch delays to respect Gemini API quotas.
- **Automatic History Persistence**: Persists batch job records, dataset counters, and individual row evaluation payloads to Supabase PostgreSQL.
- **Aggregate Analytics**: Computes pass rates, dimension score averages, Gemini API call metrics, and execution timing.
- **Dual Export Formats**: Export full dataset evaluations as CSV or executive summary PDF reports.

---

## Batch Processing Architecture

```
[ Upload CSV / PDF ] ──► [ Parser Abstraction ] ──► [ Input Validator ]
                                                             │
[ Real-Time Progress ] ◄── [ Statistics Service ] ◄── [ Rate Controller ]
                                                             │
[ History Persistence ] ◄── [ Response Validator ] ◄── [ LLM Batch Worker ]
          │
          ▼
[ CSV / PDF Exporters ]
```

---

## Supported File Formats

### CSV Format
Standard CSV with required headers:
```csv
Question,AI Response,Reference Answer
"What is Machine Learning?","ML is a field of AI focused on building systems that learn from data.","Machine learning enables systems to learn from data."
```

### Digital QA PDF Format
Searchable PDF document containing tagged or structured Q&A sections:
```text
Question: What is Deep Learning?
AI Response: Deep learning uses multi-layered artificial neural networks...
```
