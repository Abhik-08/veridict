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
        metadata: dict,
        namespace: str | None = None
    ) -> None:
        """
        Upload a single vector to Pinecone.

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

        Args:
            namespace: Namespace name.
        """

        self.index.delete(
            delete_all=True,
            namespace=namespace
        )

    def get_index_stats(self) -> dict:
        """
        Return Pinecone index statistics.
        """

        return self.index.describe_index_stats()