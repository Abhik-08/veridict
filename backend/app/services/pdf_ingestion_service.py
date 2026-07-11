import uuid
from datetime import datetime, timezone
from fastapi import UploadFile

from app.services.pdf_service import PDFService
from app.knowledge.chunkers.document_chunker import DocumentChunker
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


class PDFIngestionService:
    """
    Service responsible for ingesting uploaded PDF documents into a temporary Pinecone namespace.
    Extracts structured pages, chunks them using paragraph-aware splitting, embeds them,
    and uploads to Pinecone with rich metadata.
    """

    def __init__(self):
        self.pdf_service = PDFService()
        self.chunker = DocumentChunker()
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()

    async def ingest_pdf(self, pdf_file: UploadFile) -> dict:
        """
        Extract, chunk, embed, and upload a PDF with rich metadata and full statistics tracking.

        Args:
            pdf_file: Uploaded PDF file.

        Returns:
            dict: Statistics of the ingestion process:
                  {
                      "namespace": "...",
                      "filename": "...",
                      "pages": int,
                      "characters": int,
                      "paragraphs": int,
                      "chunks_uploaded": int
                  }
        """
        namespace = f"pdf_{uuid.uuid4().hex[:8]}"

        # 1. Extract structured pages
        extracted_pages = await self.pdf_service.extract_pages(pdf_file)

        # Calculate statistics
        total_pages = len(extracted_pages)
        total_characters = sum(len(page["text"]) for page in extracted_pages)
        total_paragraphs = 0
        for page in extracted_pages:
            paragraphs = [p.strip() for p in page["text"].split("\n\n") if p.strip()]
            total_paragraphs += len(paragraphs)

        # 2. Chunk document (page & paragraph aware)
        document = {
            "id": namespace,
            "source": "uploaded_pdf",
            "filename": pdf_file.filename or "unknown.pdf",
            "pages": extracted_pages
        }

        chunks = self.chunker.chunk_document(document)

        uploaded = 0

        # 3. Generate embeddings and upload to Pinecone
        for chunk in chunks:
            embedding = self.embedding_service.generate_embedding(chunk["text"])

            # Enrich Pinecone metadata with all required explainability fields
            metadata = {
                "source": "uploaded_pdf",
                "filename": pdf_file.filename or "unknown.pdf",
                "text": chunk["text"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk["metadata"]["page_number"],
                "chunk_character_count": chunk["metadata"]["chunk_character_count"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "namespace": namespace
            }

            self.pinecone_service.upsert_vector(
                vector_id=chunk["chunk_id"],
                embedding=embedding,
                metadata=metadata,
                namespace=namespace
            )

            uploaded += 1

        return {
            "namespace": namespace,
            "filename": pdf_file.filename or "unknown.pdf",
            "pages": total_pages,
            "characters": total_characters,
            "paragraphs": total_paragraphs,
            "chunks_uploaded": uploaded
        }