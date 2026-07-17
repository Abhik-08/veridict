import uuid
import logging
from datetime import datetime, timezone
from fastapi import UploadFile, BackgroundTasks

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    RelevanceEvaluationResult,
    AccuracyEvaluationResult,
    HallucinationEvaluationResult
)
from app.schemas.retrieval import RetrievedChunk
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.retrieval_service import RetrievalService
from app.agents.relevance_judge import RelevanceJudge
from app.agents.accuracy_judge import AccuracyJudge
from app.agents.hallucination_judge import HallucinationJudge
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
        self.accuracy_judge = AccuracyJudge()
        self.hallucination_judge = HallucinationJudge()

    async def _ingest_pdf(
        self,
        pdf_file: UploadFile,
        background_tasks: BackgroundTasks | None = None
    ) -> tuple[str, str]:
        """Handle caching check and background task scheduling for PDF ingestion."""
        pdf_bytes = await pdf_file.read()
        await pdf_file.seek(0)

        # Compute hash fingerprint
        file_hash = self.pdf_ingestion_service.cache_service.compute_hash(pdf_bytes)

        # 1. Check cache HIT/MISS
        cached = self.pdf_ingestion_service.cache_service.get_cached_namespace(file_hash)

        if cached is not None:
            # Cache HIT - Reuse namespace immediately
            return cached["namespace"], "Completed"

        # Cache MISS - Generate namespace and process
        pdf_namespace = f"pdf_{uuid.uuid4().hex[:8]}"
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
            return pdf_namespace, "Processing"
        else:
            # Synchronous fallback if no background tasks enqueued
            await self.pdf_ingestion_service.ingest_pdf_async(
                pdf_bytes,
                filename,
                pdf_namespace,
                file_hash
            )
            return pdf_namespace, "Completed"

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
            pdf_namespace, pdf_status = await self._ingest_pdf(pdf_file, background_tasks)

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
        # Evaluate response accuracy
        # -------------------------------------------------
        accuracy_eval = None
        try:
            retrieved_evidence = "\n\n".join(c.text for c in retrieved_chunks) if retrieved_chunks else None
            accuracy_res = self.accuracy_judge.evaluate_accuracy(
                question=request.question,
                ai_response=request.ai_response,
                reference_answer=request.reference_answer,
                retrieved_evidence=retrieved_evidence
            )
            accuracy_eval = AccuracyEvaluationResult(
                accuracy_score=accuracy_res.result.accuracy_score,
                reasoning=accuracy_res.result.reasoning,
                model_used=accuracy_res.model_used
            )
        except (JudgeLLMConfigurationError, ValueError):
            raise
        except Exception:
            logger.exception("Temporary Accuracy Judge unavailability encountered.")

        # -------------------------------------------------
        # Evaluate response hallucination
        # -------------------------------------------------
        hallucination_eval = None
        try:
            retrieved_evidence = "\n\n".join(c.text for c in retrieved_chunks) if retrieved_chunks else None
            hallucination_res = self.hallucination_judge.evaluate_hallucination(
                question=request.question,
                ai_response=request.ai_response,
                reference_answer=request.reference_answer,
                retrieved_evidence=retrieved_evidence
            )
            hallucination_eval = HallucinationEvaluationResult(
                hallucination_score=hallucination_res.result.hallucination_score,
                reasoning=hallucination_res.result.reasoning,
                model_used=hallucination_res.model_used
            )
        except (JudgeLLMConfigurationError, ValueError):
            raise
        except Exception:
            logger.exception("Temporary Hallucination Judge unavailability encountered.")

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
            relevance_evaluation=relevance_eval,
            accuracy_evaluation=accuracy_eval,
            hallucination_evaluation=hallucination_eval
        )