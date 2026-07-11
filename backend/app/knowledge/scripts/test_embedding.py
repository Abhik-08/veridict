from app.services.embedding_service import EmbeddingService


def main():
    service = EmbeddingService()

    text = "Artificial Intelligence is transforming healthcare."

    try:
        embedding = service.generate_embedding(text)

        print("=" * 50)
        print("Embedding Generated Successfully")
        print(f"Embedding Dimension : {len(embedding)}")
        print()

        print("First 5 Values:")

        for value in embedding[:5]:
            print(value)

        print("=" * 50)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()