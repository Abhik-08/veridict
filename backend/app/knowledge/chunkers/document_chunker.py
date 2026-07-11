from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class DocumentChunker:
    """
    Service responsible for splitting documents into chunks.

    Supports:
    - TruthfulQA (Legacy dataset chunking)
    - SQuAD (Legacy dataset chunking)
    - PDF (Page and Paragraph-aware chunking)
    - Future document sources
    """

    def __init__(
        self,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_document(self, document: dict) -> list[dict]:
        """
        Split a document into chunks.

        Expected document format:

        {
            "id": "...",
            "source": "...",
            "text": "...",             # Required for legacy/non-pdf

            # Optional / legacy dataset fields
            "question": "...",
            "answer": "...",

            # PDF fields
            "filename": "...",
            "pages": [{"page_number": int, "text": str}]
        }
        """
        source = document.get("source", "")

        # If it is an uploaded PDF and has parsed pages, perform page/paragraph-aware chunking
        if source == "uploaded_pdf" and "pages" in document:
            return self._chunk_pdf_pages(document)

        # Otherwise use standard recursive text chunking for legacy compatibility
        return self._chunk_legacy_document(document)

    def _chunk_pdf_pages(self, document: dict) -> list[dict]:
        """
        Chunk a PDF document using page and paragraph-aware constraints.
        Ensures chunks never cross page boundaries.
        """
        pages = document.get("pages", [])
        filename = document.get("filename", "unknown.pdf")
        doc_id = document.get("id", "unknown_doc")

        output_chunks = []
        global_chunk_index = 0

        for page_data in pages:
            page_number = page_data["page_number"]
            page_text = page_data["text"].strip()

            if not page_text:
                continue

            # 1. Split page into paragraphs using double newlines
            paragraphs = self._split_page_into_paragraphs(page_text)

            # 2. Merge adjacent small paragraphs to form chunks within CHUNK_SIZE limit
            merged_paragraphs = self._merge_adjacent_paragraphs(paragraphs)

            # 3. Build actual chunk dictionaries.
            global_chunk_index = self._create_chunks_from_paragraphs(
                merged_paragraphs=merged_paragraphs,
                doc_id=doc_id,
                filename=filename,
                page_number=page_number,
                global_chunk_index=global_chunk_index,
                output_chunks=output_chunks
            )

        return output_chunks

    def _split_page_into_paragraphs(self, page_text: str) -> list[str]:
        """Split page text by double newline to find paragraph boundaries."""
        return [p.strip() for p in page_text.split("\n\n") if p.strip()]

    def _merge_adjacent_paragraphs(self, paragraphs: list[str]) -> list[str]:
        """Merge adjacent small paragraphs to optimize context chunks under CHUNK_SIZE."""
        merged_paragraphs = []
        current_merged = []
        current_length = 0

        for p in paragraphs:
            spacer_len = 2 if current_merged else 0
            # If adding this paragraph keeps us within chunk size, merge it
            if current_length + spacer_len + len(p) <= settings.CHUNK_SIZE:
                current_merged.append(p)
                current_length += spacer_len + len(p)
            else:
                # Emit previous merged chunk
                if current_merged:
                    merged_paragraphs.append("\n\n".join(current_merged))
                current_merged = [p]
                current_length = len(p)

        # Emit final merged chunk
        if current_merged:
            merged_paragraphs.append("\n\n".join(current_merged))

        return merged_paragraphs

    def _create_chunks_from_paragraphs(
        self,
        merged_paragraphs: list[str],
        doc_id: str,
        filename: str,
        page_number: int,
        global_chunk_index: int,
        output_chunks: list[dict]
    ) -> int:
        """Create final chunk dictionary payloads from merged page text paragraphs."""
        for para in merged_paragraphs:
            if len(para) <= settings.CHUNK_SIZE:
                output_chunks.append(
                    self._create_pdf_chunk(
                        doc_id=doc_id,
                        filename=filename,
                        page_number=page_number,
                        chunk_index=global_chunk_index,
                        text=para
                    )
                )
                global_chunk_index += 1
            else:
                sub_chunks = self.text_splitter.split_text(para)
                for sub_chunk in sub_chunks:
                    if not sub_chunk.strip():
                        continue
                    output_chunks.append(
                        self._create_pdf_chunk(
                            doc_id=doc_id,
                            filename=filename,
                            page_number=page_number,
                            chunk_index=global_chunk_index,
                            text=sub_chunk
                        )
                    )
                    global_chunk_index += 1
        return global_chunk_index

    def _create_pdf_chunk(
        self,
        doc_id: str,
        filename: str,
        page_number: int,
        chunk_index: int,
        text: str
    ) -> dict:
        """Create structured dictionary for a PDF chunk."""
        return {
            "chunk_id": f"{doc_id}_chunk_{chunk_index}",
            "document_id": doc_id,
            "chunk_index": chunk_index,
            "text": text,
            "metadata": {
                "source": "uploaded_pdf",
                "filename": filename,
                "page_number": page_number,
                "chunk_character_count": len(text)
            }
        }

    def _chunk_legacy_document(self, document: dict) -> list[dict]:
        """Legacy recursive character chunking logic (SQuAD / TruthfulQA)."""
        text = document.get("text", "").strip()

        # Backward compatibility with existing datasets
        if not text:
            text = document.get("context", "").strip()

        if not text:
            question = document.get("question", "")
            answer = document.get("answer", "")

            text = f"Question: {question}\n\nAnswer: {answer}"

        chunks = self.text_splitter.split_text(text)

        output = []

        for index, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            output.append(
                {
                    "chunk_id": f"{document['id']}_chunk_{index}",
                    "document_id": document["id"],
                    "chunk_index": index,
                    "text": chunk,
                    "metadata": {
                        "source": document.get("source"),
                        "question": document.get("question"),
                        "answer": document.get("answer")
                    }
                }
            )

        return output