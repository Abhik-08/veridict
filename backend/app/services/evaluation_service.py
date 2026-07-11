from fastapi import UploadFile

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse
)
from app.schemas.retrieval import RetrievedChunk
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.retrieval_service import RetrievalService


class EvaluationService:
    """
    Service responsible for preparing the evaluation payload.

    If a PDF is uploaded, it is ingested into a temporary
    Pinecone namespace and used together with the permanent
    knowledge base during retrieval.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.pdf_ingestion_service = PDFIngestionService()

    async def evaluate(
        self,
        request: EvaluationRequest,
        pdf_file: UploadFile | None = None
    ) -> EvaluationResponse:
        """
        Prepare the evaluation payload.

        Args:
            request:
                Evaluation request.

            pdf_file:
                Optional uploaded PDF.

        Returns:
            EvaluationResponse containing the submitted
            inputs and retrieved knowledge chunks.
        """

        pdf_namespace = None

        # -------------------------------------------------
        # Ingest uploaded PDF (if provided)
        # -------------------------------------------------

        if pdf_file is not None:

            ingestion_result = await self.pdf_ingestion_service.ingest_pdf(
                pdf_file
            )

            pdf_namespace = ingestion_result["namespace"]

        # -------------------------------------------------
        # Retrieve relevant chunks
        # -------------------------------------------------

        retrieval_results = self.retrieval_service.retrieve(
            query=request.question,
            pdf_namespace=pdf_namespace
        )

        retrieved_chunks = [
            RetrievedChunk(**chunk)
            for chunk in retrieval_results
        ]

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------

        return EvaluationResponse(
            question=request.question,
            ai_response=request.ai_response,
            reference_answer=request.reference_answer,
            retrieved_chunks=retrieved_chunks
        )