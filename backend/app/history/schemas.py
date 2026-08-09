"""
Pydantic Schemas for Evaluation History Foundation.
Defines strict API request and response data contracts using Pydantic V2 ConfigDict.
Inherits shared pagination models from app.common.models.pagination.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.common.models.pagination import PaginationMetadata, PaginatedResponse


class HistoryItemCreate(BaseModel):
    """Payload to record a completed single or batch evaluation."""
    question: str = Field(..., description="Evaluation question / prompt")
    ai_response: str = Field(..., description="AI response text evaluated")
    reference_answer: Optional[str] = Field(None, description="Reference ground truth answer")
    retrieved_evidence: Optional[Union[List[Any], Dict[str, Any]]] = Field(
        None, description="Retrieved RAG evidence chunks or documents"
    )
    evaluation_result: Dict[str, Any] = Field(
        ..., description="Complete judge pipeline evaluation payload"
    )
    overall_score: float = Field(..., description="Combined evaluation score 0-5")
    verdict: str = Field(..., description="Final verdict: PASS, NEEDS_IMPROVEMENT, or FAIL")
    source_type: str = Field("SINGLE", description="Evaluation source: SINGLE or BATCH")
    batch_job_id: Optional[UUID] = Field(None, description="Optional associated batch job UUID")


class HistoryItemResponse(BaseModel):
    """Summarized evaluation history record representation."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    question: str
    ai_response: str
    reference_answer: Optional[str] = None
    overall_score: float
    verdict: str
    source_type: str
    batch_job_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class EvaluationDetailResponse(HistoryItemResponse):
    """Detailed evaluation record containing complete evidence and judge result payload."""
    retrieved_evidence: Optional[Union[List[Any], Dict[str, Any]]] = None
    evaluation_result: Dict[str, Any]


class BatchJobCreate(BaseModel):
    """Payload to register a new batch evaluation task."""
    filename: str = Field(..., description="Batch dataset filename")
    total_items: int = Field(0, description="Total evaluation rows in batch file")
    status: str = Field("PROCESSING", description="Batch job status")


class BatchHistoryResponse(BaseModel):
    """Batch job task record representation."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    filename: str
    status: str
    total_items: int
    completed_items: int
    average_score: float = 0.0
    created_at: datetime
    updated_at: datetime


class BatchDetailResponse(BatchHistoryResponse):
    """Detailed batch job response including linked evaluations and verdict distribution."""
    evaluations: List[HistoryItemResponse] = Field(default_factory=list)
    verdict_distribution: Dict[str, int] = Field(default_factory=dict)


class HistoryFilterParams(BaseModel):
    """Encapsulates filter, pagination, and sorting parameters for history queries."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    verdict: Optional[str] = None
    source_type: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "DESC"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    score_min: Optional[float] = Field(None, ge=0.0, le=5.0)
    score_max: Optional[float] = Field(None, ge=0.0, le=5.0)


class DashboardStatistics(BaseModel):
    """Aggregated evaluation history statistics for user dashboard."""
    total_evaluations: int = Field(0, description="Total evaluations recorded")
    total_batch_jobs: int = Field(0, description="Total batch jobs executed")
    pass_count: int = Field(0, description="Evaluated with PASS verdict")
    needs_improvement_count: int = Field(0, description="Evaluated with NEEDS_IMPROVEMENT verdict")
    fail_count: int = Field(0, description="Evaluated with FAIL verdict")
    pass_percentage: float = Field(0.0, description="Percentage of PASS verdicts")
    fail_percentage: float = Field(0.0, description="Percentage of FAIL verdicts")
    needs_improvement_percentage: float = Field(0.0, description="Percentage of NEEDS_IMPROVEMENT verdicts")
    average_score: float = Field(0.0, description="Mean overall evaluation score")
    highest_score: float = Field(0.0, description="Highest overall evaluation score recorded")
    lowest_score: float = Field(0.0, description="Lowest overall evaluation score recorded")
    average_batch_size: float = Field(0.0, description="Average total items per batch job")
    recent_activity_count: int = Field(0, description="Evaluations recorded in the last 24 hours")
    most_recent_evaluation: Optional[datetime] = Field(None, description="Timestamp of the most recent evaluation")


class AnalyticsFilterParams(BaseModel):
    """Filter parameters for analytics endpoints."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    source_type: Optional[str] = Field(None, description="Evaluation mode: SINGLE, BATCH, or ALL")
    verdict: Optional[str] = Field(None, description="Verdict filter: PASS, NEEDS_IMPROVEMENT, FAIL, or ALL")
    model: Optional[str] = Field(None, description="Model filter extracted from evaluation_result model_used")


class VerdictDistribution(BaseModel):
    """Verdict count and percentage distribution."""
    pass_count: int = 0
    needs_improvement_count: int = 0
    fail_count: int = 0
    pass_percentage: float = 0.0
    needs_improvement_percentage: float = 0.0
    fail_percentage: float = 0.0


class AverageDimensionScores(BaseModel):
    """Average scores across evaluation dimensions (1.0 to 5.0)."""
    average_relevance: float = Field(0.0, description="Mean relevance score (1-5)")
    average_accuracy: float = Field(0.0, description="Mean accuracy score (1-5)")
    average_completeness: float = Field(0.0, description="Mean completeness score (1-5)")
    average_overall_score: float = Field(0.0, description="Mean overall score (0-5)")


class HallucinationMetrics(BaseModel):
    """
    Hallucination evaluation metrics.
    Note: INSUFFICIENT_EVIDENCE status items are excluded from evaluable counts and NOT treated as hallucinated.
    Hallucinated items are evaluable evaluations where hallucination_score < 4.
    """
    evaluable_count: int = Field(0, description="Total evaluations with evaluable hallucination status (SUCCESS)")
    insufficient_evidence_count: int = Field(0, description="Total evaluations skipped due to INSUFFICIENT_EVIDENCE")
    hallucinated_count: int = Field(0, description="Total evaluable evaluations with hallucination score < 4")
    grounded_count: int = Field(0, description="Total evaluable evaluations with hallucination score >= 4")
    hallucination_rate_percentage: float = Field(0.0, description="Percentage of evaluable responses containing hallucinations")
    average_hallucination_score: float = Field(0.0, description="Mean hallucination score across evaluable items (1-5)")


class QualityTrendPoint(BaseModel):
    """Single point in time-series quality trend graph."""
    date: str = Field(..., description="Time bucket string (YYYY-MM-DD)")
    count: int = Field(0, description="Total evaluations in this time bucket")
    average_score: float = Field(0.0, description="Average overall score in this time bucket")
    pass_count: int = Field(0, description="PASS count in this time bucket")
    needs_improvement_count: int = Field(0, description="NEEDS_IMPROVEMENT count in this time bucket")
    fail_count: int = Field(0, description="FAIL count in this time bucket")


class AvailableFilterMetadata(BaseModel):
    """Metadata listing available filter options present in user's evaluation history."""
    available_models: List[str] = Field(default_factory=list, description="Unique models present in user data")
    available_source_types: List[str] = Field(default_factory=list, description="Unique source types present (SINGLE, BATCH)")
    available_verdicts: List[str] = Field(default_factory=list, description="Unique verdicts present")


class AnalyticsStatistics(BaseModel):
    """Complete analytics response structure for Milestone 4 Scoring Dashboard."""
    total_evaluations: int = Field(0, description="Total filtered evaluations count")
    verdict_distribution: VerdictDistribution = Field(default_factory=VerdictDistribution)
    average_scores: AverageDimensionScores = Field(default_factory=AverageDimensionScores)
    hallucination_metrics: HallucinationMetrics = Field(default_factory=HallucinationMetrics)
    quality_trends: List[QualityTrendPoint] = Field(default_factory=list)
    available_filters: AvailableFilterMetadata = Field(default_factory=AvailableFilterMetadata)


__all__ = [
    "HistoryItemCreate",
    "HistoryItemResponse",
    "EvaluationDetailResponse",
    "BatchJobCreate",
    "BatchHistoryResponse",
    "BatchDetailResponse",
    "HistoryFilterParams",
    "PaginationMetadata",
    "PaginatedResponse",
    "DashboardStatistics",
    "AnalyticsFilterParams",
    "VerdictDistribution",
    "AverageDimensionScores",
    "HallucinationMetrics",
    "QualityTrendPoint",
    "AvailableFilterMetadata",
    "AnalyticsStatistics",
]
