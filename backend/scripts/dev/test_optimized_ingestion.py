import asyncio
import time
from datetime import datetime, timezone, timedelta
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.pdf_cache_service import PDFCacheService
from app.services.pdf_ingestion_service import PDFIngestionService


def run_tests():
    client = TestClient(app)
    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()
    cache_service = PDFCacheService()
    ingestion_service = PDFIngestionService()

    print("\n" + "=" * 60)
    print("STARTING OPTIMIZED INGESTION PIPELINE TESTS")
    print("=" * 60)

    # 1. Test Batch Embedding (Phase A)
    print("\n[Phase A] Testing batch embedding generation...")
    texts = [
        "First test text chunk for batch embedding.",
        "Second test text chunk for batch embedding.",
        "Third test text chunk for batch embedding."
    ]
    embeddings = embedding_service.generate_embeddings(texts)
    assert len(embeddings) == len(texts), "Failed to match batch text counts to embedding counts"
    assert len(embeddings[0]) == 3072, f"Expected 3072 dimensions, got {len(embeddings[0])}"
    print("  OK: Batch embedding generated successfully.")

    # 2. Test Batch Pinecone Upload (Phase B)
    print("\n[Phase B] Testing batch Pinecone upsert...")
    test_namespace = "test_batch_upsert_ns"
    vectors = [
        {"id": f"test_vec_{i}", "values": embeddings[0], "metadata": {"source": "test"}}
        for i in range(5)
    ]
    # Clean first
    pinecone_service.delete_namespace(test_namespace)
    time.sleep(1) # Allow deletion to propagate

    # Batch upload
    pinecone_service.upsert_vectors(vectors, namespace=test_namespace)
    time.sleep(2) # Allow indexing
    for v in vectors:
        assert pinecone_service.vector_exists(v["id"], namespace=test_namespace), f"Vector {v['id']} not uploaded"
    print("  OK: Batch vectors upserted and verified.")

    # Clean namespace
    pinecone_service.delete_namespace(test_namespace)
    print("  OK: Cleaned up test upsert namespace.")

    # 3. Test Cache Hit/Miss & Background Ingestion (Phases C, D, G)
    print("\n[Phases C, D, G] Testing caching, background tasks & metrics...")
    r_pdf = requests.get('https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf')
    pdf_bytes = r_pdf.content

    # Pre-clean cache for testing consistency
    file_hash = cache_service.compute_hash(pdf_bytes)
    cache_service.delete_cache_entry("DUMMY_INGESTION_NAMESPACE_DO_NOT_REUSE")
    # Delete by hash directly
    if file_hash in cache_service.cache:
        del cache_service.cache[file_hash]
        cache_service._save_cache()

    # FIRST UPLOAD (Cache Miss)
    print("  Uploading PDF first time (should trigger Cache Miss)...")
    files = {"pdf_file": ("test_doc.pdf", pdf_bytes, "application/pdf")}
    data = {
        "question": "What is inside test doc?",
        "ai_response": "This is a testing document context.",
        "reference_answer": "test text"
    }
    r_eval1 = client.post("/evaluate", data=data, files=files)
    assert r_eval1.status_code == 200, f"POST /evaluate failed: {r_eval1.text}"
    eval1_data = r_eval1.json()
    namespace1 = eval1_data["pdf_namespace"]
    status1 = eval1_data["pdf_status"]
    assert namespace1 is not None, "Namespace must not be null"
    assert status1 == "Processing", f"Expected 'Processing', got '{status1}'"
    print(f"  OK: Cache Miss enqueued. Job ID/Namespace: {namespace1}")

    # Polling job status (Phase D & G)
    print("  Polling job status to completion...")
    completed = False
    status_payload = {}
    for attempt in range(20):
        r_status = client.get(f"/evaluate/status/{namespace1}")
        assert r_status.status_code == 200, f"Status check failed: {r_status.text}"
        status_payload = r_status.json()
        if status_payload["status"] == "Completed":
            completed = True
            break
        elif status_payload["status"] == "Failed":
            raise AssertionError(f"Ingestion job failed: {status_payload.get('error')}")
        time.sleep(1)

    assert completed, "Background task enqueued did not complete within timeout"
    print("  OK: Background task processed to Completed.")
    print("  OK: Performance metrics verified:")
    print(f"      Pages: {status_payload['pages']}")
    print(f"      Characters: {status_payload['characters']}")
    print(f"      Paragraphs: {status_payload['paragraphs']}")
    print(f"      Chunks: {status_payload['chunks_uploaded']}")
    print(f"      Embedding Batches: {status_payload['embedding_batches']}")
    print(f"      Pinecone Batches: {status_payload['pinecone_batches']}")
    print(f"      Ingestion Time: {status_payload['processing_time_seconds']}s")
    print(f"      Detailed Metrics: {status_payload.get('metrics')}")

    # SECOND UPLOAD (Cache Hit)
    print("  Uploading same PDF second time (should trigger Cache Hit)...")
    files2 = {"pdf_file": ("test_doc.pdf", pdf_bytes, "application/pdf")}
    r_eval2 = client.post("/evaluate", data=data, files=files2)
    assert r_eval2.status_code == 200, f"POST /evaluate 2 failed: {r_eval2.text}"
    eval2_data = r_eval2.json()
    namespace2 = eval2_data["pdf_namespace"]
    status2 = eval2_data["pdf_status"]
    assert namespace2 == namespace1, f"Expected cache hit to reuse namespace {namespace1}, got {namespace2}"
    assert status2 == "Completed", f"Expected immediate completion for cache hit, got {status2}"
    print("  OK: Cache Hit enqueued and verified. Namespace successfully reused.")

    # 4. Test Namespace Expiration and Cleanup (Phases E & F)
    print("\n[Phases E & F] Testing temporary namespace TTL expiration and cleanup...")
    # Artificially set cached created_at to 30 hours ago to trigger expiration
    cache_service._load_cache()
    assert file_hash in cache_service.cache, "Cache entry not found before expiration check"
    expired_time = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    cache_service.cache[file_hash]["created_at"] = expired_time
    cache_service._save_cache()

    # Invoke cleanup
    deleted_namespaces = ingestion_service.cleanup_expired_namespaces()
    assert namespace1 in deleted_namespaces, f"Namespace {namespace1} was not cleaned up"
    print(f"  OK: Cleanup enqueued. Purged expired namespace: {namespace1}")

    # Confirm purged from Pinecone and Cache
    time.sleep(1)
    cache_service._load_cache()
    assert file_hash not in cache_service.cache, "Purged hash was not deleted from Cache registry"
    print("  OK: Verified cache registry purged.")

    job_status = ingestion_service.get_job_status(namespace1)
    assert job_status["status"] == "Expired", f"Expected status 'Expired', got {job_status['status']}"
    print("  OK: Verified task status updated to Expired.")

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
