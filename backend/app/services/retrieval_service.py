from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


class RetrievalService:
    """
    Service responsible for retrieving the most relevant
    knowledge chunks from Pinecone.
    """

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()

    def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve the Top-K most relevant knowledge chunks.

        Args:
            query (str): User question.

        Returns:
            list[dict]: List of retrieved chunks with their similarity
                        scores and explicit, flattened metadata fields.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # Generate embedding for the user's query
        query_embedding = self.embedding_service.generate_embedding(query)

        # Search Pinecone
        results = self.pinecone_service.query_vectors(
            embedding=query_embedding,
            top_k=settings.TOP_K
        )

        retrieved_chunks = []

        for match in results.matches:
            metadata = match.metadata or {}
            retrieved_chunks.append(
                {
                    "id": match.id,
                    "score": match.score,
                    "source": metadata.get("source", "N/A"),
                    "document_id": metadata.get("document_id", "N/A"),
                    "chunk_index": int(metadata.get("chunk_index", 0)),
                    "question": metadata.get("question", "N/A"),
                    "answer": metadata.get("answer", "N/A"),
                    "text": metadata.get("text", "N/A"),
                }
            )

        return retrieved_chunks