from pydantic import BaseModel, Field

from app.schemas.retrieval import RetrievedChunk

_MODEL_USED_DESCRIPTION = "Gemini model used for evaluation."


class EvaluationRequest(BaseModel):
    """
    Request model for AI response evaluation.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="User's original question."
    )

    ai_response: str = Field(
        ...,
        min_length=1,
        description="AI-generated response to evaluate."
    )

    reference_answer: str | None = Field(
        default=None,
        description="Optional reference answer provided by the user."
    )


class EvaluationResponse(BaseModel):
    """
    Response model for AI response evaluation.

    This response contains the submitted inputs, retrieved knowledge chunks,
    and optional PDF background task tracking parameters.
    """

    question: str = Field(
        ...,
        description="User's original question."
    )

    ai_response: str = Field(
        ...,
        description="AI-generated response."
    )

    reference_answer: str | None = Field(
        default=None,
        description="Optional reference answer provided by the user."
    )

    retrieved_chunks: list[RetrievedChunk] = Field(
        default_factory=list,
        description="Relevant knowledge chunks retrieved from the knowledge base."
    )

    pdf_namespace: str | None = Field(
        default=None,
        description="Pinecone namespace containing the ingested PDF context."
    )

    pdf_status: str | None = Field(
        default=None,
        description="Ingestion status of the uploaded PDF: Pending, Processing, Completed, Failed."
    )

    relevance_evaluation: "RelevanceEvaluationResult | None" = Field(
        default=None,
        description="Relevance judge evaluation result, or null if unavailable."
    )

    accuracy_evaluation: "AccuracyEvaluationResult | None" = Field(
        default=None,
        description="Accuracy judge evaluation result, or null if unavailable."
    )

    hallucination_evaluation: "HallucinationEvaluationResult | None" = Field(
        default=None,
        description="Hallucination judge evaluation result, or null if unavailable."
    )


class RelevanceEvaluationResult(BaseModel):
    """Result of the Relevance Judge evaluation."""

    relevance_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Relevance score (1-5)."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="Reasoning explaining the relevance score."
    )

    model_used: str = Field(
        ...,
        description=_MODEL_USED_DESCRIPTION
    )


class AccuracyEvaluationResult(BaseModel):
    """Result of the Accuracy Judge evaluation."""

    accuracy_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Accuracy score (1-5)."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="Reasoning explaining the accuracy score."
    )

    model_used: str = Field(
        ...,
        description=_MODEL_USED_DESCRIPTION
    )


class HallucinationEvaluationResult(BaseModel):
    """Result of the Hallucination Judge evaluation."""

    status: str = Field(
        default="SUCCESS",
        description="Evaluation outcome status: 'SUCCESS' or 'INSUFFICIENT_EVIDENCE'."
    )

    hallucination_score: int | None = Field(
        default=None,
        description="Hallucination score (1-5), or null when status is INSUFFICIENT_EVIDENCE."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="Reasoning explaining the hallucination score or why evidence was insufficient."
    )

    model_used: str = Field(
        ...,
        description=_MODEL_USED_DESCRIPTION
    )