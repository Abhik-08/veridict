from app.services.retrieval_service import RetrievalService


def main() -> None:
    """
    Test script for verifying semantic retrieval capability.
    Loads query from user prompt, retrieves relevant chunks, and prints them.
    Supports printing PDF page details, metadata, and previews.
    """
    retrieval_service = RetrievalService()

    query = input("Enter your question: ")

    try:
        results = retrieval_service.retrieve(query)

        print("\n" + "=" * 60)
        print("Top Retrieved Chunks")
        print("=" * 60)

        if not results:
            print("No matching chunks found.")
            return

        for i, result in enumerate(results, start=1):
            print(f"\nResult #{i}")
            print("-" * 40)
            print(f"Score       : {result['score']:.4f}")
            print(f"Chunk ID    : {result['id']}")
            print(f"Source      : {result['source']}")
            print(f"Doc ID      : {result['document_id']}")
            print(f"Chunk Index : {result['chunk_index']}")
            print(f"Question    : {result['question']}")
            print(f"Answer      : {result['answer']}")
            if result.get("filename"):
                print(f"Filename    : {result['filename']}")
                print(f"Page Number : {result['page_number']}")
                print(f"Namespace   : {result['namespace']}")
                print(f"Created At  : {result['created_at']}")
            print(f"Preview     : {result['preview']}")
            print(f"Text        : {result['text']}")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()