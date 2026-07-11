"""
Veridict — Fault-Tolerant Pinecone Ingestion Pipeline

Features:
    - Automatic resume from last checkpoint
    - Google quota detection (429 RESOURCE_EXHAUSTED)
    - Crash-safe progress saving (after every upload)
    - Duplicate protection via checkpoint + Pinecone verification
    - Graceful CTRL+C handling
    - Idempotent — safe to run multiple times
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


# ==============================
# Configuration
# ==============================
INPUT_FILE: str = "app/knowledge/processed/chunks.json"
PROGRESS_FILE: str = "app/knowledge/processed/ingestion_progress.json"

# Testing Mode
TEST_MODE: bool = False
TEST_LIMIT: int = 10

# Reset Progress (set True to restart from chunk 0)
RESET_PROGRESS: bool = False

# Flag for graceful shutdown
_interrupted: bool = False


# ==============================
# Signal Handler
# ==============================

def _handle_interrupt(signum: int, frame) -> None:
    """Set the interrupt flag so the main loop exits cleanly."""
    global _interrupted
    _interrupted = True


# ==============================
# Helper Functions
# ==============================

def load_chunks() -> list[dict]:
    """
    Load chunks from the input file.

    Returns:
        List of chunk dictionaries.
    """

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks: list[dict] = json.load(f)

    if TEST_MODE:
        chunks = chunks[:TEST_LIMIT]

    return chunks


def load_progress() -> dict:
    """
    Load ingestion progress from checkpoint file.

    Returns:
        Progress dictionary, or empty defaults if no checkpoint exists.
    """

    if RESET_PROGRESS and os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("Progress file deleted. Starting from chunk 0.")
        print()

    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "last_completed_chunk_index": -1,
        "last_completed_chunk_id": None,
        "successful_uploads": 0,
        "last_run": None
    }


def save_progress(
    chunk_index: int,
    chunk_id: str,
    successful_uploads: int
) -> None:
    """
    Save current ingestion progress to checkpoint file.

    Called after every successful upload so at most one chunk
    is lost on crash, power failure, or quota exhaustion.

    Args:
        chunk_index: The index of the last successfully uploaded chunk.
        chunk_id: The chunk_id of the last successfully uploaded chunk.
        successful_uploads: Running total of successful uploads this session.
    """

    progress = {
        "last_completed_chunk_index": chunk_index,
        "last_completed_chunk_id": chunk_id,
        "successful_uploads": successful_uploads,
        "last_run": datetime.now(timezone.utc).isoformat()
    }

    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=4)


def find_resume_position(
    chunks: list[dict],
    progress: dict,
    pinecone_service: PineconeService
) -> int:
    """
    Determine which chunk index to resume from.

    Primary mechanism: checkpoint (last_completed_chunk_index + chunk_id).
    Secondary mechanism: if chunk_id mismatches at the saved index,
    search for the chunk_id in the list and verify via Pinecone.

    Args:
        chunks: Full list of chunks.
        progress: Progress dictionary from checkpoint file.
        pinecone_service: PineconeService instance for verification.

    Returns:
        The index to resume from (0-based into the chunks list).
    """

    last_index: int = progress["last_completed_chunk_index"]
    last_id: str | None = progress["last_completed_chunk_id"]

    # Fresh start
    if last_index < 0 or last_id is None:
        return 0

    # Verify checkpoint consistency
    if last_index < len(chunks) and chunks[last_index]["chunk_id"] == last_id:
        resume_at = last_index + 1
        print(f"Checkpoint valid. Resuming from chunk {resume_at}/{len(chunks)}.")
        print()
        return resume_at

    # Mismatch — chunks.json may have changed
    print(f"WARNING: Chunk ID mismatch at index {last_index}.")
    print(f"  Expected : {last_id}")
    if last_index < len(chunks):
        print(f"  Found    : {chunks[last_index]['chunk_id']}")
    print("Searching for last completed chunk by ID...")

    for i, chunk in enumerate(chunks):
        if chunk["chunk_id"] == last_id:
            # Verify it actually exists in Pinecone
            if pinecone_service.vector_exists(last_id):
                resume_at = i + 1
                print(f"Found and verified in Pinecone. Resuming from chunk {resume_at}.")
                print()
                return resume_at
            else:
                print(f"Found at index {i} but NOT in Pinecone. Resuming from {i}.")
                print()
                return i

    # Chunk ID not found at all — start over
    print("Could not locate last completed chunk. Starting from 0.")
    print()
    return 0


def build_metadata(chunk: dict) -> dict:
    """
    Build the Pinecone metadata payload from a chunk.

    Preserves the existing metadata schema exactly.

    Args:
        chunk: A single chunk dictionary.

    Returns:
        Metadata dictionary for Pinecone upsert.
    """

    return {
        "text": chunk["text"],
        "question": chunk["metadata"]["question"],
        "answer": chunk["metadata"]["answer"],
        "source": chunk["metadata"]["source"],
        "document_id": chunk["document_id"],
        "chunk_index": chunk["chunk_index"]
    }


def is_quota_error(error: Exception) -> bool:
    """
    Detect Google Embedding API quota/rate-limit errors.

    Checks for 429 status codes, RESOURCE_EXHAUSTED, and
    quota-related error messages.

    Args:
        error: The caught exception.

    Returns:
        True if this is a quota exhaustion error.
    """

    error_str = str(error).lower()

    quota_indicators = [
        "429",
        "resource_exhausted",
        "quota",
        "rate limit",
        "too many requests",
        "retryinfo",
    ]

    return any(indicator in error_str for indicator in quota_indicators)


def print_summary(
    total_chunks: int,
    attempted: int,
    uploaded: int,
    skipped: int,
    failed: int,
    last_index: int,
    last_chunk_id: str | None,
    next_index: int,
    chunks: list[dict],
    elapsed: float,
    stats: dict
) -> None:
    """
    Print the final upload summary and Pinecone index statistics.

    Args:
        total_chunks: Total number of chunks in the dataset.
        attempted: Number of chunks attempted this session.
        uploaded: Number of chunks successfully uploaded.
        skipped: Number of chunks skipped (already existed).
        failed: Number of chunks that failed.
        last_index: Index of the last uploaded chunk.
        last_chunk_id: Chunk ID of the last uploaded chunk.
        next_index: The next chunk index to resume from.
        chunks: Full chunk list (for resolving next chunk ID).
        elapsed: Elapsed time in seconds.
        stats: Pinecone index stats dictionary.
    """

    next_chunk_id = chunks[next_index]["chunk_id"] if next_index < len(chunks) else "N/A (Complete)"

    minutes, seconds = divmod(int(elapsed), 60)

    print()
    print("=" * 60)
    print("Upload Summary")
    print("=" * 60)
    print(f"  Total Chunks          : {total_chunks}")
    print(f"  Chunks Attempted      : {attempted}")
    print(f"  Uploaded              : {uploaded}")
    print(f"  Skipped (Duplicates)  : {skipped}")
    print(f"  Failed                : {failed}")
    print(f"  Last Uploaded Index   : {last_index}")
    print(f"  Last Uploaded Chunk ID: {last_chunk_id or 'N/A'}")
    print(f"  Next Resume Index     : {next_index}")
    print(f"  Next Resume Chunk     : {next_chunk_id}")
    print(f"  Elapsed Time          : {minutes}m {seconds}s")
    print("=" * 60)
    print()
    print("Pinecone Index Statistics")
    print("-" * 40)
    print(f"  Dimension    : {stats.get('dimension', 'N/A')}")
    print(f"  Namespaces   : {stats.get('namespaces', {})}")
    print(f"  Vector Count : {stats.get('total_vector_count', 'N/A')}")
    print(f"  Metric       : {stats.get('metric', 'N/A')}")
    print("=" * 60)


# ==============================
# Main Pipeline
# ==============================

def main() -> None:
    """
    Fault-tolerant ingestion pipeline.

    Pipeline:
        Load chunks → Load progress → Find resume position →
        For each chunk: Check Pinecone → Embed → Upload → Checkpoint →
        On quota: Save & exit → Tomorrow: Resume automatically.
    """

    global _interrupted

    # Register CTRL+C handler
    signal.signal(signal.SIGINT, _handle_interrupt)

    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()

    # Load data
    chunks = load_chunks()
    total_chunks = len(chunks)

    # Load and resolve resume position
    progress = load_progress()
    resume_from = find_resume_position(chunks, progress, pinecone_service)

    if resume_from >= total_chunks:
        print("All chunks already uploaded. Nothing to do.")
        stats = pinecone_service.get_index_stats()
        print_summary(
            total_chunks=total_chunks,
            attempted=0, uploaded=0, skipped=0, failed=0,
            last_index=progress["last_completed_chunk_index"],
            last_chunk_id=progress["last_completed_chunk_id"],
            next_index=total_chunks, chunks=chunks,
            elapsed=0.0, stats=stats
        )
        return

    remaining = total_chunks - resume_from

    print("=" * 60)
    print(f"Uploading {remaining} chunks to Pinecone...")
    print(f"  Total chunks   : {total_chunks}")
    print(f"  Resuming from  : {resume_from}")
    print(f"  Remaining      : {remaining}")
    print("=" * 60)
    print()

    # Counters
    uploaded: int = 0
    skipped: int = 0
    failed: int = 0
    attempted: int = 0
    last_uploaded_index: int = progress["last_completed_chunk_index"]
    last_uploaded_id: str | None = progress["last_completed_chunk_id"]

    start_time = time.time()

    for i in range(resume_from, total_chunks):

        # Check for CTRL+C
        if _interrupted:
            print()
            print("-" * 60)
            print("Upload Interrupted by User (CTRL+C)")
            print("Progress Saved. Resume Later.")
            print("-" * 60)
            break

        chunk = chunks[i]
        chunk_id = chunk["chunk_id"]
        attempted += 1

        try:
            # Generate embedding
            print("-" * 48)
            print(f"  Chunk          : {i + 1} / {total_chunks}")
            print(f"  Chunk ID       : {chunk_id}")
            print("  Generating Embedding...")

            embedding = embedding_service.generate_embedding(chunk["text"])

            # Upload to Pinecone
            print("  Uploading...")

            metadata = build_metadata(chunk)

            pinecone_service.upsert_vector(
                vector_id=chunk_id,
                embedding=embedding,
                metadata=metadata
            )

            uploaded += 1
            last_uploaded_index = i
            last_uploaded_id = chunk_id

            # Immediate checkpoint
            save_progress(
                chunk_index=i,
                chunk_id=chunk_id,
                successful_uploads=progress["successful_uploads"] + uploaded
            )

            print("  Upload Successful")

        except Exception as e:

            # Quota detection — save and exit immediately
            if is_quota_error(e):
                print()
                print("=" * 60)
                print("  Google Embedding API Daily Quota Reached")
                print("  Progress Saved Successfully")
                print("  Resume Tomorrow")
                print("=" * 60)
                break

            # Non-quota error — log and continue
            failed += 1
            print(f"  FAILED : {e}")

    elapsed = time.time() - start_time

    # Determine next resume position
    next_index = last_uploaded_index + 1 if last_uploaded_index >= 0 else 0

    # Final stats
    stats = pinecone_service.get_index_stats()

    print_summary(
        total_chunks=total_chunks,
        attempted=attempted,
        uploaded=uploaded,
        skipped=skipped,
        failed=failed,
        last_index=last_uploaded_index,
        last_chunk_id=last_uploaded_id,
        next_index=next_index,
        chunks=chunks,
        elapsed=elapsed,
        stats=stats
    )


if __name__ == "__main__":
    main()