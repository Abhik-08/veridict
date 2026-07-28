"""
Veridict Batch Evaluation Schemas.

Defines internal QA pair models, per-row evaluation result models,
and batch progress tracking schemas for the Batch Evaluation Module.
"""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class BatchQAPairInput(BaseModel):
    """Normalized QA pair input parsed from CSV or Digital QA PDF."""
    id: str = Field(..., description="Unique ID for the QA pair (e.g. QA-01)")
    row_index: int = Field(..., description="1-indexed row number in the upload dataset")
    question: str = Field(..., description="Original user question or prompt")
    ai_response: str = Field(..., description="AI response to be evaluated")
    reference_answer: str | None = Field(None, description="Optional ground-truth reference answer")


class BatchItemEvaluationResult(BaseModel):
    """Detailed evaluation result for an individual QA pair in a batch."""
    id: str
    row_index: int
    question: str
    ai_response: str
    reference_answer: str | None = None
    evidence_text: str | None = None
    evidence_source: str = Field("NO_EVIDENCE", description="REFERENCE_ANSWER, EVIDENCE_PDF, KNOWLEDGE_BASE, or NO_EVIDENCE")
    relevance_score: float = Field(0.0, ge=0.0, le=5.0)
    accuracy_score: float = Field(0.0, ge=0.0, le=5.0)
    hallucination_score: float | None = Field(None, description="None if INSUFFICIENT_EVIDENCE")
    completeness_score: float = Field(0.0, ge=0.0, le=5.0)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    overall_score: float = Field(0.0, ge=0.0, le=5.0)
    verdict: str = Field("FAIL", description="PASS, NEEDS_IMPROVEMENT, or FAIL")
    reasoning: str = Field("", description="Concise evaluation summary for this item")
    status: Literal["COMPLETED", "FAILED"] = "COMPLETED"
    error_message: str | None = None


class BatchProgress(BaseModel):
    """Real-time progress status of an active or completed batch evaluation job."""
    batch_id: str
    filename: str
    file_type: Literal["CSV", "PDF"]
    total_rows: int
    processed_rows: int
    remaining_rows: int
    current_batch: int
    total_batches: int
    completed_count: int = 0
    failed_count: int = 0
    status: Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"] = "PENDING"
    error_message: str | None = None
    items: list[BatchItemEvaluationResult] = Field(default_factory=list)

    # Job Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    started_at: str | None = None
    finished_at: str | None = None
    elapsed_seconds: float = 0.0
    retry_count: int = 0
    gemini_call_count: int = 0
    statistics: dict[str, Any] | None = None
