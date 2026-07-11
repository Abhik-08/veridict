from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


def main():

    embedding_service = EmbeddingService()
    pinecone_service = PineconeService()

    text = "Artificial Intelligence is transforming healthcare."

    embedding = embedding_service.generate_embedding(text)

    metadata = {
        "text": text,
        "source": "test"
    }

    pinecone_service.upsert_vector(
        vector_id="test-vector",
        embedding=embedding,
        metadata=metadata
    )

    print("=" * 50)
    print("Vector uploaded successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()