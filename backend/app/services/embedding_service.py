from google import genai

from app.core.config import settings


class EmbeddingService:
    """
    Service responsible for generating text embeddings
    using Google's Embedding API.
    """

    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.

        Args:
            text (str): Input text

        Returns:
            list[float]: Embedding vector
        """

        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        response = self.client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
        )

        return response.embeddings[0].values

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts in batches using Google's Embedding API.

        Args:
            texts (list[str]): Input list of text strings.

        Returns:
            list[list[float]]: List of embedding vectors.
        """
        if not texts:
            return []

        # Ensure all texts are non-empty
        for text in texts:
            if not text or not text.strip():
                raise ValueError("Input texts list cannot contain empty strings.")

        embeddings = []
        batch_size = settings.EMBEDDING_BATCH_SIZE

        # Process texts in chunks of EMBEDDING_BATCH_SIZE
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=batch,
            )
            for emb in response.embeddings:
                embeddings.append(emb.values)

        return embeddings