from google import genai

from app.core.config import settings


class EmbeddingService:
    """
    Service responsible for generating text embeddings
    using Google's Embedding API.
    """

    def __init__(self):
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