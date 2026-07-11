import logging
from pinecone import Pinecone

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        metadata: dict,
        namespace: str | None = None
    ) -> None:
        """
        Upload a single vector.

        Args:
            vector_id: Unique identifier.
            embedding: Embedding values.
            metadata: Metadata.
            namespace: Optional namespace.
        """

        kwargs = {
            "vectors": [
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }
            ]
        }

        if namespace:
            kwargs["namespace"] = namespace

        self.index.upsert(**kwargs)

    def upsert_vectors(
        self,
        vectors: list[dict],
        namespace: str | None = None
    ) -> None:
        """
        Upload multiple vectors in batches.

        Args:
            vectors: List of dictionaries matching the format:
                     [{"id": str, "values": list[float], "metadata": dict}]
            namespace: Optional namespace.
        """
        if not vectors:
            return

        batch_size = settings.UPSERT_BATCH_SIZE

        # Upload in batches of size UPSERT_BATCH_SIZE
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            kwargs = {
                "vectors": batch
            }
            if namespace:
                kwargs["namespace"] = namespace

            self.index.upsert(**kwargs)

    def vector_exists(
        self,
        vector_id: str,
        namespace: str | None = None
    ) -> bool:
        """
        Check whether a vector exists.

        Args:
            vector_id: Vector ID.
            namespace: Optional namespace.

        Returns:
            True if found.
        """

        kwargs = {
            "ids": [vector_id]
        }

        if namespace:
            kwargs["namespace"] = namespace

        result = self.index.fetch(**kwargs)

        return vector_id in result.vectors

    def query_vectors(
        self,
        embedding: list[float],
        top_k: int = settings.TOP_K,
        namespace: str | None = None
    ):
        """
        Search Pinecone for similar vectors.

        Args:
            embedding: Query embedding.
            top_k: Number of results.
            namespace: Optional namespace.

        Returns:
            Pinecone query response.
        """

        kwargs = {
            "vector": embedding,
            "top_k": top_k,
            "include_metadata": True
        }

        if namespace:
            kwargs["namespace"] = namespace

        return self.index.query(**kwargs)

    def delete_namespace(
        self,
        namespace: str
    ) -> None:
        """
        Delete all vectors inside a namespace.
        Handles errors gracefully if the namespace does not exist.

        Args:
            namespace: Namespace name.
        """
        try:
            self.index.delete(
                delete_all=True,
                namespace=namespace
            )
        except Exception as e:
            logger.warning(f"Failed to delete namespace '{namespace}' (may not exist): {e}")

    def get_index_stats(self) -> dict:
        """
        Return Pinecone index statistics.
        """

        return self.index.describe_index_stats()