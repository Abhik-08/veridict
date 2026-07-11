import json
import os

from app.services.embedding_service import EmbeddingService


INPUT_FILE = "app/knowledge/processed/chunks.json"
OUTPUT_FILE = "app/knowledge/processed/embedded_chunks.json"

# ==============================
# Testing Configuration
# ==============================
TEST_MODE = True
TEST_LIMIT = 10


def main():
    embedding_service = EmbeddingService()

    # Load chunks
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    # Use only a small sample while testing
    if TEST_MODE:
        chunks = chunks[:TEST_LIMIT]

    embedded_chunks = []

    successful = 0
    failed = 0
    embedding_dimension = 0

    print("=" * 60)
    print(f"Generating embeddings for {len(chunks)} chunks...")
    print("=" * 60)

    for index, chunk in enumerate(chunks, start=1):

        try:
            embedding = embedding_service.generate_embedding(chunk["text"])

            embedding_dimension = len(embedding)

            embedded_chunks.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"],
                }
            )

            successful += 1

            print(f"[{index}/{len(chunks)}] Embedded successfully")

        except Exception as e:
            failed += 1
            print(f"[{index}/{len(chunks)}] Failed : {e}")

    # Create output folder if needed
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Save embeddings
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            embedded_chunks,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\n" + "=" * 60)
    print("Embedding Generation Completed")
    print("=" * 60)
    print(f"Chunks Read          : {len(chunks)}")
    print(f"Successful           : {successful}")
    print(f"Failed               : {failed}")
    print(f"Embedding Dimension  : {embedding_dimension}")
    print(f"Saved To             : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()