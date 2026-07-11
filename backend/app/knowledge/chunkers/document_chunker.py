import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentChunker:
    def __init__(self, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_document(self, document):
        """
        Splits one document into multiple chunks.
        """

        text = document.get("context", "")

        chunks = self.text_splitter.split_text(text)

        output = []

        for index, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            output.append({
                "chunk_id": str(uuid.uuid4()),
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