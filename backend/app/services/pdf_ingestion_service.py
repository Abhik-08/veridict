import uuid
import json
import os
import time
from datetime import datetime, timezone
import logging
from fastapi import UploadFile

from app.core.config import settings
from app.services.pdf_service import PDFService
from app.knowledge.chunkers.document_chunker import DocumentChunker
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.pdf_cache_service import PDFCacheService

logger = logging.getLogger(__name__)

UNKNOWN_PDF = "unknown.pdf"


class PDFIngestionService:
    """
    Service responsible for ingesting uploaded PDF documents into a temporary Pinecone namespace.
    Supports both synchronous processing and FastAPI BackgroundTasks execution with job status tracking.
    """

    def __init__(self) -> None:
        self.pdf_service = PDFService()
        self.chunker = DocumentChunker()
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()
        self.cache_service = PDFCacheService()
        self.jobs_file = settings.INGESTION_JOBS_FILE
        self._load_jobs()

    def _load_jobs(self) -> None:
        """Load job tracking registry from the JSON file."""
        if os.path.exists(self.jobs_file):
            try:
                with open(self.jobs_file, "r", encoding="utf-8") as f:
                    self.jobs = json.load(f)
            except Exception:
                logger.exception("Failed to load ingestion jobs file")
                self.jobs = {}
        else:
            self.jobs = {}

    def _save_jobs(self) -> None:
        """Save job tracking registry to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.jobs_file), exist_ok=True)
            with open(self.jobs_file, "w", encoding="utf-8") as f:
                json.dump(self.jobs, f, indent=4, ensure_ascii=False)
        except Exception:
            logger.exception("Failed to save ingestion jobs file")

    def get_job_status(self, namespace: str) -> dict | None:
        """Retrieve the current processing state and stats for an ingestion namespace."""
        self._load_jobs()
        return self.jobs.get(namespace)

    def update_job_status(self, namespace: str, status: str, **kwargs) -> None:
        """Update job metrics and save state to disk."""
        self._load_jobs()
        job = self.jobs.get(namespace, {})
        job.update({
            "namespace": namespace,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **kwargs
        })
        self.jobs[namespace] = job
        self._save_jobs()

    async def ingest_pdf(self, pdf_file: UploadFile) -> dict:
        """
        Extract, chunk, embed, and upload a PDF synchronously (Legacy/Testing compatibility).

        Args:
            pdf_file: Uploaded PDF file.

        Returns:
            dict: Statistics of the ingestion process.
        """
        filename = pdf_file.filename or UNKNOWN_PDF
        logger.info(f"Synchronously ingesting PDF: {filename}")
        start_time = time.perf_counter()

        extracted_pages = await self.pdf_service.extract_pages(pdf_file)

        total_pages = len(extracted_pages)
        total_characters = sum(len(page["text"]) for page in extracted_pages)
        total_paragraphs = sum(
            len([p.strip() for p in page["text"].split("\n\n") if p.strip()])
            for page in extracted_pages
        )

        document = {
            "id": f"pdf_sync_{uuid.uuid4().hex[:8]}",
            "source": "uploaded_pdf",
            "filename": filename,
            "pages": extracted_pages
        }

        chunks = self.chunker.chunk_document(document)

        # Batch embedding generation
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.generate_embeddings(texts)

        # Batch Pinecone upsert
        vectors = []
        namespace = document["id"]
        for idx, chunk in enumerate(chunks):
            vectors.append({
                "id": chunk["chunk_id"],
                "values": embeddings[idx],
                "metadata": {
                    "source": "uploaded_pdf",
                    "filename": filename,
                    "text": chunk["text"],
                    "document_id": chunk["document_id"],
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk["metadata"]["page_number"],
                    "chunk_character_count": chunk["metadata"]["chunk_character_count"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "namespace": namespace
                }
            })

        self.pinecone_service.upsert_vectors(vectors, namespace=namespace)
        total_duration = time.perf_counter() - start_time

        embedding_batches = (len(chunks) + settings.EMBEDDING_BATCH_SIZE - 1) // settings.EMBEDDING_BATCH_SIZE
        pinecone_batches = (len(chunks) + settings.UPSERT_BATCH_SIZE - 1) // settings.UPSERT_BATCH_SIZE

        return {
            "namespace": namespace,
            "filename": filename,
            "pages": total_pages,
            "characters": total_characters,
            "paragraphs": total_paragraphs,
            "chunks_uploaded": len(chunks),
            "embedding_batches": embedding_batches,
            "pinecone_batches": pinecone_batches,
            "processing_time_seconds": round(total_duration, 2)
        }

    async def ingest_pdf_async(
        self,
        pdf_bytes: bytes,
        filename: str,
        namespace: str,
        file_hash: str
    ) -> None:
        """
        Background task to process PDF document parsing, embedding, and storage.

        Args:
            pdf_bytes: Raw bytes content of the PDF.
            filename: Original PDF filename.
            namespace: Destination temporary namespace.
            file_hash: Computed SHA256 of the PDF content.
        """
        logger.info(f"Starting background ingestion for {filename} -> namespace {namespace}")
        start_time = time.perf_counter()

        try:
            from io import BytesIO
            dummy_file = UploadFile(
                file=BytesIO(pdf_bytes),
                filename=filename,
                headers={"content-type": "application/pdf"}
            )

            # 1. Page extraction
            t_start = time.perf_counter()
            extracted_pages = await self.pdf_service.extract_pages(dummy_file)
            t_ext = time.perf_counter() - t_start

            total_pages = len(extracted_pages)
            total_characters = sum(len(page["text"]) for page in extracted_pages)
            total_paragraphs = 0
            for page in extracted_pages:
                paragraphs = [p.strip() for p in page["text"].split("\n\n") if p.strip()]
                total_paragraphs += len(paragraphs)

            # 2. Paragraph-aware chunking
            t_start = time.perf_counter()
            document = {
                "id": namespace,
                "source": "uploaded_pdf",
                "filename": filename,
                "pages": extracted_pages
            }
            chunks = self.chunker.chunk_document(document)
            t_chunk = time.perf_counter() - t_start

            # 3. Batch embeddings
            t_start = time.perf_counter()
            texts = [c["text"] for c in chunks]
            embeddings = self.embedding_service.generate_embeddings(texts)
            t_embed = time.perf_counter() - t_start

            embedding_batches = (len(chunks) + settings.EMBEDDING_BATCH_SIZE - 1) // settings.EMBEDDING_BATCH_SIZE

            # 4. Batch upsert
            t_start = time.perf_counter()
            vectors = []
            for idx, chunk in enumerate(chunks):
                vectors.append({
                    "id": chunk["chunk_id"],
                    "values": embeddings[idx],
                    "metadata": {
                        "source": "uploaded_pdf",
                        "filename": filename,
                        "text": chunk["text"],
                        "document_id": chunk["document_id"],
                        "chunk_index": chunk["chunk_index"],
                        "page_number": chunk["metadata"]["page_number"],
                        "chunk_character_count": chunk["metadata"]["chunk_character_count"],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "namespace": namespace
                    }
                })

            self.pinecone_service.upsert_vectors(vectors, namespace=namespace)
            t_upload = time.perf_counter() - t_start

            pinecone_batches = (len(chunks) + settings.UPSERT_BATCH_SIZE - 1) // settings.UPSERT_BATCH_SIZE
            total_duration = time.perf_counter() - start_time

            # Update Cache registry
            self.cache_service.cache_namespace(
                file_hash=file_hash,
                namespace=namespace,
                filename=filename,
                pages=total_pages,
                character_count=total_characters
            )

            # Mark status Completed
            self.update_job_status(
                namespace,
                "Completed",
                pages=total_pages,
                characters=total_characters,
                paragraphs=total_paragraphs,
                chunks_uploaded=len(chunks),
                embedding_batches=embedding_batches,
                pinecone_batches=pinecone_batches,
                processing_time_seconds=round(total_duration, 2),
                metrics={
                    "extraction_time": round(t_ext, 2),
                    "chunking_time": round(t_chunk, 2),
                    "embedding_time": round(t_embed, 2),
                    "upload_time": round(t_upload, 2)
                }
            )
            logger.info(f"Ingestion completed for {filename} in {total_duration:.2f}s")

        except Exception:
            logger.exception(f"Background ingestion failed for namespace {namespace}")
            self.update_job_status(namespace, "Failed", error=f"Background ingestion failed for namespace {namespace}")

    def cleanup_expired_namespaces(self) -> list[str]:
        """
        Scan all cached namespaces and delete those whose TTL has expired.
        Purges Pinecone vectors, deletes the cache entries, and updates the registry.

        Returns:
            list[str]: Names of deleted namespaces.
        """
        logger.info("Starting check for expired PDF namespaces...")
        self.cache_service._load_cache()
        self._load_jobs()

        deleted = []
        ttl_seconds = settings.PDF_NAMESPACE_TTL_HOURS * 3600

        # Create a copy of cache items to iterate over since we'll modify it
        cache_items = list(self.cache_service.cache.items())

        for file_hash, entry in cache_items:
            created_at_str = entry.get("created_at")
            if not created_at_str:
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str)
                # Compute elapsed time
                elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()

                if elapsed > ttl_seconds:
                    namespace = entry["namespace"]
                    logger.info(f"Purging expired namespace: {namespace} (elapsed: {elapsed / 3600:.2f} hours)")

                    # 1. Delete Pinecone namespace
                    try:
                        self.pinecone_service.delete_namespace(namespace)
                    except Exception:
                        logger.exception(f"Failed to delete Pinecone namespace {namespace}")

                    # 2. Delete cache record
                    self.cache_service.delete_cache_entry(namespace)

                    # 3. Update job status registry
                    if namespace in self.jobs:
                        self.jobs[namespace]["status"] = "Expired"
                        self.jobs[namespace]["deleted_at"] = datetime.now(timezone.utc).isoformat()
                    
                    deleted.append(namespace)

            except Exception:
                logger.exception(f"Error checking expiration for hash {file_hash}")

        if deleted:
            self._save_jobs()

        logger.info(f"Cleanup finished. Total expired namespaces deleted: {len(deleted)}")
        return deleted