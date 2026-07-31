"""
Veridict Batch Evaluation Orchestrator Service.

Manages evidence resolution, batching (groups of 3), execution of combined
LLM calls, deterministic Python verdict calculation, and thread-safe progress tracking.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.schemas.batch_evaluation import (
    BatchItemEvaluationResult,
    BatchProgress,
    BatchQAPairInput,
)
from app.services.batch_validator import BatchInputValidator
from app.services.batch_llm_service import BatchLLMService
from app.services.batch_rate_controller import BatchRateController
from app.services.batch_statistics_service import BatchStatisticsService
from app.services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)


class BatchEvaluationService:
    """Orchestrates batch processing jobs, evidence resolution, and state updates."""

    _jobs_store: dict[str, BatchProgress] = {}

    def __init__(self) -> None:
        self.batch_llm_service = BatchLLMService()
        self.pinecone_service = PineconeService()
        self.rate_controller = BatchRateController(max_concurrency=1, inter_batch_delay=0.2)

    @classmethod
    def get_progress(cls, batch_id: str) -> BatchProgress | None:
        return cls._jobs_store.get(batch_id)

    def create_job(
        self,
        filename: str,
        file_type: str,
        items: list[BatchQAPairInput],
        user_id: Any | None = None,
        db: Any | None = None,
    ) -> BatchProgress:
        # Pre-evaluation Input Validation
        validated_items = BatchInputValidator.validate(items)

        batch_id = f"BATCH-{uuid.uuid4().hex[:8]}"
        total_rows = len(validated_items)
        total_batches = (total_rows + settings.BATCH_SIZE - 1) // settings.BATCH_SIZE

        # Persist DB BatchJob record if authenticated user and db session provided
        db_batch_id = None
        if user_id and db:
            try:
                from app.history.service import HistoryService
                db_job = HistoryService.create_batch_job(
                    db=db,
                    user_id=user_id,
                    data={"filename": filename, "total_items": total_rows, "status": "PROCESSING"},
                )
                db_batch_id = db_job.id
                logger.info("Batch job created | job_id=%s | total_items=%d", db_batch_id, total_rows)
            except Exception as batch_err:
                logger.warning("History persistence failed for batch job creation: %s", batch_err)

        progress = BatchProgress(
            batch_id=batch_id,
            filename=filename,
            file_type=file_type,  # type: ignore
            total_rows=total_rows,
            processed_rows=0,
            remaining_rows=total_rows,
            current_batch=0,
            total_batches=total_batches,
            completed_count=0,
            failed_count=0,
            status="PENDING",
            created_at=datetime.now().isoformat(),
            db_batch_id=db_batch_id,
        )
        self._jobs_store[batch_id] = progress
        return progress

    def _persist_single_item(
        self,
        item_result: BatchItemEvaluationResult,
        batch_id: str,
        progress: BatchProgress,
        user_id: Any | None,
        db: Any | None,
        db_batch_id: Any | None,
    ) -> None:
        """Transparently persists completed batch item result to user history."""
        if not (user_id and db and item_result.status == "COMPLETED"):
            return
        try:
            from app.history.service import HistoryService
            item_dict = item_result.model_dump() if hasattr(item_result, "model_dump") else item_result.dict()
            HistoryService.create_evaluation(
                db=db,
                user_id=user_id,
                data=item_dict,
                source_type="BATCH",
                batch_job_id=db_batch_id,
            )
            logger.info(
                "Batch item evaluation persisted | batch=%s | completed=%d/%d",
                batch_id,
                progress.completed_count,
                progress.total_rows,
            )
        except Exception as item_persist_exc:
            logger.warning("History persistence failed for batch item: %s", item_persist_exc)

    def _process_single_chunk(
        self,
        chunk: list[dict[str, Any]],
        batch_num: int,
        total_chunks: int,
        batch_id: str,
        progress: BatchProgress,
        user_id: Any | None,
        db: Any | None,
        db_batch_id: Any | None,
    ) -> None:
        """Processes a single batch chunk of items."""
        progress.current_batch = batch_num
        self.rate_controller.acquire_slot_sync()
        logger.info(f"Processing Batch {batch_num}/{total_chunks} containing {len(chunk)} items...")

        try:
            eval_results_list = self.batch_llm_service.evaluate_batch(chunk)
            progress.gemini_call_count += 1
            eval_map = {res["id"]: res for res in eval_results_list if "id" in res}

            for item_data in chunk:
                item_id = item_data["id"]
                res_data = eval_map.get(item_id, {})

                item_result = self._calculate_python_verdict(item_data, res_data)
                progress.items.append(item_result)

                if item_result.status == "COMPLETED":
                    progress.completed_count += 1
                else:
                    progress.failed_count += 1

                self._persist_single_item(item_result, batch_id, progress, user_id, db, db_batch_id)

        except Exception as exc:
            logger.exception(f"Batch {batch_num} failed completely: {str(exc)}")
            progress.retry_count += 1
            for item_data in chunk:
                failed_item = BatchItemEvaluationResult(
                    id=item_data["id"],
                    row_index=item_data["row_index"],
                    question=item_data["question"],
                    ai_response=item_data["ai_response"],
                    reference_answer=item_data.get("reference_answer"),
                    evidence_text=item_data.get("evidence_text"),
                    evidence_source=item_data.get("evidence_source", "NO_EVIDENCE"),
                    status="FAILED",
                    error_message=f"Batch processing error: {str(exc)}",
                )
                progress.items.append(failed_item)
                progress.failed_count += 1

    def process_batch_job(
        self,
        batch_id: str,
        items: list[BatchQAPairInput],
        pdf_namespace: str | None = None,
        user_id: Any | None = None,
        db: Any | None = None,
        db_batch_id: Any | None = None,
    ) -> None:
        """Background task function that processes all batches sequentially."""
        progress = self._jobs_store.get(batch_id)
        if not progress:
            logger.error(f"Batch job '{batch_id}' not found in job store.")
            return

        start_time = time.time()
        progress.status = "PROCESSING"
        progress.started_at = datetime.now().isoformat()
        logger.info(f"Starting Batch Job '{batch_id}' with {len(items)} items across {progress.total_batches} batches.")

        try:
            # 1. Resolve evidence for all items before batching
            resolved_items = []
            for item in items:
                evidence_text, evidence_source = self._resolve_evidence(item, pdf_namespace)
                resolved_items.append({
                    "id": item.id,
                    "row_index": item.row_index,
                    "question": item.question,
                    "ai_response": item.ai_response,
                    "reference_answer": item.reference_answer,
                    "evidence_text": evidence_text,
                    "evidence_source": evidence_source,
                })

            # 2. Chunk into batches of BATCH_SIZE (3)
            chunks = [
                resolved_items[i : i + settings.BATCH_SIZE]
                for i in range(0, len(resolved_items), settings.BATCH_SIZE)
            ]

            for batch_num, chunk in enumerate(chunks, start=1):
                self._process_single_chunk(
                    chunk, batch_num, len(chunks), batch_id, progress, user_id, db, db_batch_id
                )
                progress.processed_rows = len(progress.items)
                progress.remaining_rows = progress.total_rows - progress.processed_rows

            elapsed = time.time() - start_time
            progress.elapsed_seconds = round(elapsed, 2)
            progress.finished_at = datetime.now().isoformat()
            progress.status = "COMPLETED"

            # Calculate Batch Statistics
            progress.statistics = BatchStatisticsService.calculate_statistics(
                items=progress.items,
                elapsed_seconds=progress.elapsed_seconds,
                gemini_calls=progress.gemini_call_count,
            )

            logger.info(
                f"Batch Job '{batch_id}' finished successfully in {progress.elapsed_seconds}s. "
                f"Completed: {progress.completed_count}, Failed: {progress.failed_count}"
            )

        except Exception as global_exc:
            logger.exception(f"Fatal error in Batch Job '{batch_id}': {str(global_exc)}")
            progress.status = "FAILED"
            progress.finished_at = datetime.now().isoformat()
            progress.error_message = str(global_exc)

    def _resolve_evidence(
        self, item: BatchQAPairInput, pdf_namespace: str | None
    ) -> tuple[str | None, str]:
        """
        Evidence Resolution Priority:
        1. Reference Answer
        2. Evidence PDF namespace
        3. Permanent RAG Knowledge Base
        4. No Evidence
        """
        if item.reference_answer and item.reference_answer.strip():
            return item.reference_answer.strip(), "REFERENCE_ANSWER"

        if pdf_namespace:
            try:
                chunks = self.pinecone_service.query_chunks(
                    query=item.question,
                    namespace=pdf_namespace,
                    top_k=3,
                )
                if chunks:
                    evidence = "\n---\n".join([c.chunk_text for c in chunks])
                    return evidence, "EVIDENCE_PDF"
            except Exception as e:
                logger.warning(f"PDF evidence query failed for item {item.id}: {str(e)}")

        try:
            chunks = self.pinecone_service.query_chunks(
                query=item.question,
                top_k=3,
            )
            if chunks:
                evidence = "\n---\n".join([c.chunk_text for c in chunks])
                return evidence, "KNOWLEDGE_BASE"
        except Exception as e:
            logger.warning(f"Knowledge Base query failed for item {item.id}: {str(e)}")

        return None, "NO_EVIDENCE"

    def _calculate_python_verdict(
        self, item_data: dict[str, Any], res_data: dict[str, Any]
    ) -> BatchItemEvaluationResult:
        """Calculate weighted score and verdict in Python deterministically."""
        rel_score = float(res_data.get("relevance_score", 3.0))
        acc_score = float(res_data.get("accuracy_score", 3.0))
        comp_score = float(res_data.get("completeness_score", 3.0))
        reasoning = res_data.get("reasoning", "Evaluation complete.")

        hal_score_raw = res_data.get("hallucination_score")
        hal_score: float | None = float(hal_score_raw) if hal_score_raw is not None else None

        # Python Weight Normalization
        if hal_score is not None:
            weights = {"relevance": 0.35, "accuracy": 0.35, "hallucination": 0.15, "completeness": 0.15}
            raw_weighted = (
                rel_score * weights["relevance"]
                + acc_score * weights["accuracy"]
                + hal_score * weights["hallucination"]
                + comp_score * weights["completeness"]
            )
        else:
            weights = {"relevance": 0.4118, "accuracy": 0.4118, "completeness": 0.1764}
            raw_weighted = (
                rel_score * weights["relevance"]
                + acc_score * weights["accuracy"]
                + comp_score * weights["completeness"]
            )

        overall_score = round(raw_weighted, 2)

        # Category Mapping
        if overall_score >= 4.50:
            verdict = "PASS"
        elif overall_score >= 3.50:
            verdict = "NEEDS_IMPROVEMENT"
        else:
            verdict = "FAIL"

        return BatchItemEvaluationResult(
            id=item_data["id"],
            row_index=item_data["row_index"],
            question=item_data["question"],
            ai_response=item_data["ai_response"],
            reference_answer=item_data.get("reference_answer"),
            evidence_text=item_data.get("evidence_text"),
            evidence_source=item_data.get("evidence_source", "NO_EVIDENCE"),
            relevance_score=rel_score,
            accuracy_score=acc_score,
            hallucination_score=hal_score,
            completeness_score=comp_score,
            overall_score=overall_score,
            verdict=verdict,
            reasoning=reasoning,
            status="COMPLETED",
        )
