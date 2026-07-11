from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class DocumentChunker:
    def __init__(self, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_document(self, document):
        """
        Splits one document into multiple chunks.
        """

        text = document.get("context", "").strip()

        # TruthfulQA documents have empty context — use Q+A instead
        if not text:
            text = f"Question: {document['question']}\n\nAnswer: {document['answer']}"

        chunks = self.text_splitter.split_text(text)

        output = []

        for index, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            output.append({
                "chunk_id": f"{document['id']}_chunk_{index}",
                "document_id": document["id"],
                "chunk_index": index,
                "text": chunk,
                "metadata": {
                    "question": document["question"],
                    "answer": document["answer"],
                    "source": document["source"]
                }
            })

        return output