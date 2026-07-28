# Knowledge Base

This directory contains the RAG (Retrieval-Augmented Generation) knowledge base infrastructure used by Veridict for evidence-based AI response evaluation.

## Structure

- **datasets/** — Raw benchmark datasets
  - `squad/` — SQuAD (Stanford Question Answering Dataset)
  - `truthfulqa/` — TruthfulQA dataset
- **chunkers/** — Document chunking utilities
  - `document_chunker.py` — Splits documents into semantic chunks for embedding
- **preprocessors/** — Data cleaning and normalization
  - `data_cleaner.py` — Input data sanitization
  - `normalizer.py` — Text normalization utilities
  - `sampler.py` — Dataset sampling utilities
- **validators/** — Data quality validation
  - `knowledge_validator.py` — Validates knowledge base integrity
- **scripts/** — Knowledge base build pipeline
  - `download_datasets.py` — Downloads benchmark datasets from Hugging Face
  - `build_knowledge_base.py` — Builds the unified knowledge base from raw datasets
  - `build_chunks.py` — Generates semantic chunks from knowledge base documents
  - `generate_embeddings.py` — Computes embedding vectors for chunks
  - `ingest_to_pinecone.py` — Upserts embedded chunks to Pinecone vector database
- **processed/** — Generated runtime artifacts (gitignored)
  - `chunks.json` — Processed document chunks
  - `knowledge_base.json` — Unified knowledge base
  - `pdf_cache.json` — PDF ingestion cache registry
  - `ingestion_jobs.json` — Background ingestion job state
