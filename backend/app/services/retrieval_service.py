from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


class RetrievalService:
    """
    Service responsible for retrieving the most relevant
    knowledge chunks from Pinecone.

    Supports retrieval from:
    - Default namespace (TruthfulQA + SQuAD)
    - Optional uploaded PDF namespace
    """

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()

    def retrieve(
        self,
        query: str,
        pdf_namespace: str | None = None
    ) -> list[dict]:
        """
        Retrieve the Top-K most relevant knowledge chunks.

        Searches:
        1. Default namespace (TruthfulQA + SQuAD)
        2. Optional uploaded PDF namespace

        Results from both are merged, sorted by similarity,
        and the overall Top-K are returned.

        Args:
            query: User question.
            pdf_namespace: Optional uploaded PDF namespace.

        Returns:
            list[dict]: List of retrieved chunks.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # ----------------------------------------
        # Generate embedding for the query
        # ----------------------------------------
        query_embedding = self.embedding_service.generate_embedding(query)

        all_matches = []

        # ----------------------------------------
        # Search Default Namespace (TruthfulQA + SQuAD)
        # ----------------------------------------
        knowledge_results = self.pinecone_service.query_vectors(
            embedding=query_embedding,
            top_k=settings.TOP_K
        )
        all_matches.extend(knowledge_results.matches)

        # ----------------------------------------
        # Search Uploaded PDF Namespace
        # ----------------------------------------
        if pdf_namespace:
            pdf_results = self.pinecone_service.query_vectors(
                embedding=query_embedding,
                top_k=settings.TOP_K,
                namespace=pdf_namespace
            )
            all_matches.extend(pdf_results.matches)

        # ----------------------------------------
        # Sort by similarity
        # ----------------------------------------
        all_matches.sort(
            key=lambda match: match.score,
            reverse=True
        )

        # ----------------------------------------
        # Keep overall Top-K
        # ----------------------------------------
        top_matches = all_matches[:settings.TOP_K]

        retrieved_chunks = []

        for match in top_matches:
            metadata = match.metadata or {}
            text = metadata.get("text", "N/A")

            # Generate 150-200 char preview (using 180 char cut-off)
            preview = text[:180] + "..." if len(text) > 180 else text

            retrieved_chunks.append(
                {
                    "id": match.id,
                    "score": float(match.score),
                    "source": metadata.get("source", "N/A"),
                    "document_id": metadata.get("document_id", "N/A"),
                    "chunk_index": int(metadata.get("chunk_index", 0)),
                    "question": metadata.get("question", "N/A"),
                    "answer": metadata.get("answer", "N/A"),
                    "text": text,
                    # Optional PDF / Rich document metadata fields
                    "filename": metadata.get("filename"),
                    "page_number": int(metadata.get("page_number")) if "page_number" in metadata else None,
                    "chunk_character_count": int(metadata.get("chunk_character_count")) if "chunk_character_count" in metadata else None,
                    "created_at": metadata.get("created_at"),
                    "namespace": metadata.get("namespace"),
                    "preview": preview,
                }
            )

        return retrieved_chunks