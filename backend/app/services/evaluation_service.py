import uuid
import logging
from datetime import datetime, timezone
from fastapi import UploadFile, BackgroundTasks

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    RelevanceEvaluationResult
)
from app.schemas.retrieval import RetrievedChunk
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.retrieval_service import RetrievalService
from app.agents.relevance_judge import RelevanceJudge
from app.core.exceptions import JudgeLLMConfigurationError

logger = logging.getLogger(__name__)

UNKNOWN_PDF = "unknown.pdf"


class EvaluationService:
    """
    Service responsible for preparing the evaluation payload.

    Supports fingerprint caching and asynchronous background ingestion of PDFs
    using FastAPI BackgroundTasks.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.pdf_ingestion_service = PDFIngestionService()
        self.relevance_judge = RelevanceJudge()

    async def evaluate(
        self,
        request: EvaluationRequest,
        pdf_file: UploadFile | None = None,
        background_tasks: BackgroundTasks | None = None
    ) -> EvaluationResponse:
        """
        Prepare the evaluation payload, integrating caching and background task scheduling.

        Args:
            request: Evaluation request.
            pdf_file: Optional uploaded PDF.
            background_tasks: FastAPI BackgroundTasks registry.

        Returns:
            EvaluationResponse containing inputs, retrieval chunks, and job status.
        """
        pdf_namespace = None
        pdf_status = None

        # -------------------------------------------------
        # Ingest uploaded PDF (if provided)
        # -------------------------------------------------
        if pdf_file is not None:
            pdf_bytes = await pdf_file.read()
            await pdf_file.seek(0)

            # Compute hash fingerprint
            file_hash = self.pdf_ingestion_service.cache_service.compute_hash(pdf_bytes)

            # 1. Check cache HIT/MISS
            cached = self.pdf_ingestion_service.cache_service.get_cached_namespace(file_hash)

            if cached is not None:
                # Cache HIT - Reuse namespace immediately
                pdf_namespace = cached["namespace"]
                pdf_status = "Completed"
            else:
                # Cache MISS - Generate namespace and process
                pdf_namespace = f"pdf_{uuid.uuid4().hex[:8]}"
                pdf_status = "Processing"

                filename = pdf_file.filename or UNKNOWN_PDF

                # Initialize job status as Pending
                self.pdf_ingestion_service.update_job_status(
                    namespace=pdf_namespace,
                    status="Pending",
                    filename=filename,
                    created_at=datetime.now(timezone.utc).isoformat()
                )

                # 2. Dispatch to background or execute synchronously
                if background_tasks is not None:
                    background_tasks.add_task(
                        self.pdf_ingestion_service.ingest_pdf_async,
                        pdf_bytes,
                        filename,
                        pdf_namespace,
                        file_hash
                    )
                else:
                    # Synchronous fallback if no background tasks enqueued
                    await self.pdf_ingestion_service.ingest_pdf_async(
                        pdf_bytes,
                        filename,
                        pdf_namespace,
                        file_hash
                    )
                    pdf_status = "Completed"

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
        # Evaluate response relevance
        # -------------------------------------------------
        relevance_eval = None
        try:
            judge_res = self.relevance_judge.evaluate_relevance(
                question=request.question,
                ai_response=request.ai_response
            )
            relevance_eval = RelevanceEvaluationResult(
                relevance_score=judge_res.result.relevance_score,
                reasoning=judge_res.result.reasoning,
                model_used=judge_res.model_used
            )
        except (JudgeLLMConfigurationError, ValueError):
            raise
        except Exception:
            logger.exception("Temporary Relevance Judge unavailability encountered.")

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------
        return EvaluationResponse(
            question=request.question,
            ai_response=request.ai_response,
            reference_answer=request.reference_answer,
            retrieved_chunks=retrieved_chunks,
            pdf_namespace=pdf_namespace,
            pdf_status=pdf_status,
            relevance_evaluation=relevance_eval
        )