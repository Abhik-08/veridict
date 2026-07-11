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