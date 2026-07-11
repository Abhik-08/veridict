from pydantic import BaseModel, Field

from app.schemas.retrieval import RetrievedChunk


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

    This response does not perform evaluation yet.
    It simply returns the submitted inputs along with
    the retrieved knowledge chunks that will be used
    by the Judge Agents in future phases.
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