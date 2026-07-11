from pinecone import Pinecone

from app.core.config import settings


class PineconeService:
    """
    Service responsible for interacting with Pinecone.
    """

    def __init__(self):
        self.pc = Pinecone(
            api_key=settings.PINECONE_API_KEY
        )

        self.index = self.pc.Index(
            settings.PINECONE_INDEX_NAME
        )

    def upsert_vector(
        self,
        vector_id: str,
        embedding: list[float],
        metadata: dict
    ) -> None:
        """
        Upload a single vector to Pinecone.

        Args:
            vector_id: Unique identifier for the vector.
            embedding: The embedding values.
            metadata: Metadata to store alongside the vector.
        """

        self.index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }
            ]
        )

    def vector_exists(self, vector_id: str) -> bool:
        """
        Check whether a vector already exists in Pinecone.

        Uses fetch() which returns only the requested ID
        without scanning the entire index.

        Args:
            vector_id: The vector ID to check.

        Returns:
            True if the vector exists, False otherwise.
        """

        result = self.index.fetch(ids=[vector_id])
        return vector_id in result.vectors

    def query_vectors(
        self,
        embedding: list[float],
        top_k: int = settings.TOP_K
    ):
        """
        Search Pinecone for the most similar vectors.

        Args:
            embedding: Query embedding.
            top_k: Number of similar chunks to retrieve.

        Returns:
            Pinecone query response containing the most
            relevant vectors and their metadata.
        """

        return self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )

    def get_index_stats(self) -> dict:
        """
        Return Pinecone index statistics.

        Returns:
            Dictionary containing index dimension,
            vector count, namespaces, and metric information.
        """

        return self.index.describe_index_stats()