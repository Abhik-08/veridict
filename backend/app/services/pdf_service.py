from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.config import settings


class PDFService:
    """
    Service responsible for extracting text from uploaded PDF documents.
    Supports both raw text joining and structured page-by-page extraction.
    """

    async def extract_pages(self, pdf_file: UploadFile) -> list[dict]:
        """
        Extract text page-by-page from an uploaded PDF.

        Args:
            pdf_file: Uploaded PDF file.

        Returns:
            list[dict]: List of dictionaries containing page_number (1-based)
                        and page text content.

        Raises:
            ValueError: If the file is not a PDF, is encrypted, corrupted,
                        empty, too large, or contains no readable text.
        """
        self._validate_file_type(pdf_file)

        try:
            pdf_bytes = await pdf_file.read()
            await pdf_file.seek(0)  # Reset stream pointer

            # Validate byte size limit
            if len(pdf_bytes) > settings.MAX_PDF_SIZE_BYTES:
                raise ValueError(
                    f"Extremely large PDF file is not supported. "
                    f"Max size allowed: {settings.MAX_PDF_SIZE_BYTES // (1024 * 1024)}MB."
                )

            reader = PdfReader(BytesIO(pdf_bytes))
            self._validate_pdf_reader(reader)

            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text_content = page_text.strip() if page_text else ""
                extracted_pages.append({
                    "page_number": i + 1,
                    "text": text_content
                })

            # Verify that some readable text content exists
            if not any(len(p["text"]) > 0 for p in extracted_pages):
                raise ValueError("No readable text found in the uploaded PDF.")

            return extracted_pages

        except PdfReadError:
            raise ValueError("Invalid or corrupted PDF file.")
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

    async def extract_text(self, pdf_file: UploadFile) -> str:
        """
        Extract text from an uploaded PDF and join pages with double newlines.

        Args:
            pdf_file: Uploaded PDF file.

        Returns:
            Extracted text as a single string.
        """
        pages = await self.extract_pages(pdf_file)
        return "\n\n".join([p["text"] for p in pages if p["text"]])

    def _validate_file_type(self, pdf_file: UploadFile) -> None:
        """Enforce that uploaded files are actually PDF format."""
        if pdf_file.content_type is not None:
            if pdf_file.content_type != "application/pdf":
                raise ValueError("Only PDF files are supported.")
        else:
            if (
                pdf_file.filename is None
                or not pdf_file.filename.lower().endswith(".pdf")
            ):
                raise ValueError("Only PDF files are supported.")

    def _validate_pdf_reader(self, reader: PdfReader) -> None:
        """Validate encryption status, blank structure, and maximum page limits."""
        if reader.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported.")

        if not reader.pages:
            raise ValueError("Empty PDF document.")

        if len(reader.pages) > settings.MAX_PDF_PAGES:
            raise ValueError(
                f"Extremely large PDF file is not supported. "
                f"Max pages allowed: {settings.MAX_PDF_PAGES}."
            )