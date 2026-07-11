import json
import os

from app.knowledge.chunkers.document_chunker import DocumentChunker


def main():
    # File paths
    input_file = "app/knowledge/processed/knowledge_base.json"
    output_file = "app/knowledge/processed/chunks.json"

    # Load knowledge base
    with open(input_file, "r", encoding="utf-8") as f:
        documents = json.load(f)

    chunker = DocumentChunker()

    all_chunks = []
    total_docs = len(documents)

    # Chunk each document
    for i, document in enumerate(documents, start=1):
        if i % 100 == 0:
            print(f"Chunking document {i}/{total_docs}...")

        chunks = chunker.chunk_document(document)
        all_chunks.extend(chunks)

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save chunks
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4, ensure_ascii=False)

    # Chunk statistics
    chunk_lengths = [len(c["text"]) for c in all_chunks]
    avg_chunks = len(all_chunks) / total_docs if total_docs else 0

    print()
    print("=" * 50)
    print(f"Documents Processed : {total_docs}")
    print(f"Chunks Generated    : {len(all_chunks)}")
    print(f"Average Chunks/Doc  : {avg_chunks:.2f}")
    print(f"Largest Chunk       : {max(chunk_lengths)} characters")
    print(f"Smallest Chunk      : {min(chunk_lengths)} characters")
    print(f"Saved To            : {output_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()