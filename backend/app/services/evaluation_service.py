import asyncio
import uuid
import logging
from datetime import datetime, timezone
from fastapi import UploadFile, BackgroundTasks

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    RelevanceEvaluationResult,
    AccuracyEvaluationResult,
    HallucinationEvaluationResult,
    CompletenessEvaluationResult
)
from app.schemas.judge import VerdictOutput
from app.schemas.retrieval import RetrievedChunk
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.retrieval_service import RetrievalService
from app.agents.relevance_judge import RelevanceJudge
from app.agents.accuracy_judge import AccuracyJudge
from app.agents.hallucination_judge import HallucinationJudge
from app.agents.completeness_judge import CompletenessJudge
from app.agents.verdict_agent import VerdictAgent
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
        self.completeness_judge = CompletenessJudge()
        self.verdict_agent = VerdictAgent()

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

        logger.info("Evaluation pipeline started.")

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

        retrieved_evidence = "\n\n".join(c.text for c in retrieved_chunks) if retrieved_chunks else None

        # -------------------------------------------------
        # Concurrently Evaluate Response (Parallel Judge LLM Execution)
        # -------------------------------------------------
        def run_relevance():
            try:
                judge_res = self.relevance_judge.evaluate_relevance(
                    question=request.question,
                    ai_response=request.ai_response
                )
                return RelevanceEvaluationResult(
                    relevance_score=judge_res.result.relevance_score,
                    reasoning=judge_res.result.reasoning,
                    model_used=judge_res.model_used
                )
            except (JudgeLLMConfigurationError, ValueError):
                raise
            except Exception:
                logger.exception("Temporary Relevance Judge unavailability encountered.")
                return None

        def run_accuracy():
            try:
                accuracy_res = self.accuracy_judge.evaluate_accuracy(
                    question=request.question,
                    ai_response=request.ai_response,
                    reference_answer=request.reference_answer,
                    retrieved_evidence=retrieved_evidence
                )
                return AccuracyEvaluationResult(
                    accuracy_score=accuracy_res.result.accuracy_score,
                    reasoning=accuracy_res.result.reasoning,
                    model_used=accuracy_res.model_used
                )
            except (JudgeLLMConfigurationError, ValueError):
                raise
            except Exception:
                logger.exception("Temporary Accuracy Judge unavailability encountered.")
                return None

        def run_hallucination():
            try:
                hallucination_res = self.hallucination_judge.evaluate_hallucination(
                    question=request.question,
                    ai_response=request.ai_response,
                    reference_answer=request.reference_answer,
                    retrieved_evidence=retrieved_evidence
                )
                return HallucinationEvaluationResult(
                    status=hallucination_res.result.status,
                    hallucination_score=hallucination_res.result.hallucination_score,
                    reasoning=hallucination_res.result.reasoning,
                    model_used=hallucination_res.model_used
                )
            except (JudgeLLMConfigurationError, ValueError):
                raise
            except Exception:
                logger.exception("Temporary Hallucination Judge unavailability encountered.")
                return None

        def run_completeness():
            try:
                completeness_res = self.completeness_judge.evaluate_completeness(
                    question=request.question,
                    ai_response=request.ai_response
                )
                return CompletenessEvaluationResult(
                    completeness_score=completeness_res.result.completeness_score,
                    reasoning=completeness_res.result.reasoning,
                    covered_aspects=completeness_res.result.covered_aspects,
                    missing_aspects=completeness_res.result.missing_aspects,
                    model_used=completeness_res.model_used
                )
            except (JudgeLLMConfigurationError, ValueError):
                raise
            except Exception:
                logger.exception("Temporary Completeness Judge unavailability encountered.")
                return None

        # Execute 4 Judge Agents in parallel worker threads
        results = await asyncio.gather(
            asyncio.to_thread(run_relevance),
            asyncio.to_thread(run_accuracy),
            asyncio.to_thread(run_hallucination),
            asyncio.to_thread(run_completeness),
            return_exceptions=True
        )

        relevance_eval = results[0] if not isinstance(results[0], Exception) else None
        accuracy_eval = results[1] if not isinstance(results[1], Exception) else None
        hallucination_eval = results[2] if not isinstance(results[2], Exception) else None
        completeness_eval = results[3] if not isinstance(results[3], Exception) else None

        # Raise configuration/validation errors if any judge raised them
        for res in results:
            if isinstance(res, (JudgeLLMConfigurationError, ValueError)):
                raise res

        # -------------------------------------------------
        # Synthesize overall evaluation verdict
        # -------------------------------------------------
        verdict_eval = None
        try:
            verdict_eval = self.verdict_agent.generate_verdict(
                question=request.question,
                ai_response=request.ai_response,
                accuracy_eval=accuracy_eval,
                completeness_eval=completeness_eval,
                relevance_eval=relevance_eval,
                hallucination_eval=hallucination_eval
            )
        except (JudgeLLMConfigurationError, ValueError):
            raise
        except Exception:
            logger.exception("Temporary Verdict Agent unavailability encountered.")

        logger.info("Evaluation pipeline completed.")

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
            hallucination_evaluation=hallucination_eval,
            completeness_evaluation=completeness_eval,
            verdict_evaluation=verdict_eval
        )