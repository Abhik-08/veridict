# Veridict RAG Pipeline & Vector Search

Veridict uses a Retrieval-Augmented Generation (RAG) architecture to ground AI response evaluation in verifiable factual evidence.

---

## RAG Architecture Overview

```
[ Raw Benchmark Datasets / User PDFs ]
                 │
                 ▼
     [ Semantic Chunking Engine ]
                 │
                 ▼
  [ Google Embedding API (001) ]
                 │
                 ▼
  [ Pinecone Vector DB Namespace ]
                 │
                 ▼
     [ Semantic Similarity Search ]
                 │
                 ▼
[ Retrieved Evidence Context → Judges ]
```

---

## Key Pipeline Components

1. **Benchmark Ingestion**:
   - Downloads and preprocesses SQuAD and TruthfulQA benchmark datasets.
   - Cleans text, normalizes whitespace, and samples representative QA pairs.

2. **Semantic Chunking**:
   - `DocumentChunker` breaks text into overlapping semantic passages (500 chars, 100 char overlap).

3. **Batch Embedding**:
   - Generates 768-dimensional dense vector embeddings via Google `gemini-embedding-001`.

4. **Pinecone Vector Database**:
   - Index name: `veridict-knowledge-base`.
   - Supports default global namespace for benchmark knowledge and dynamic temporary namespaces for user-uploaded PDFs.

5. **PDF Ingestion & Caching**:
   - MD5 fingerprint caching to avoid re-embedding identical PDF documents.
   - Background ingestion with real-time status monitoring.
   - Scheduled hourly cleanup task purging expired temporary namespaces (TTL: 24h).
