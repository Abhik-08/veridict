from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    """
    Request model for semantic retrieval.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="User question for semantic search."
    )


class RetrievedChunk(BaseModel):
    """
    Represents a single retrieved knowledge chunk with explicit flattened fields.
    """

    id: str = Field(..., description="Unique identifier for the chunk.")
    score: float = Field(..., description="Similarity score from semantic search.")
    source: str = Field(..., description="Source dataset of the chunk (e.g., squad, truthfulqa).")
    document_id: str = Field(..., description="Unique identifier of the source document.")
    chunk_index: int = Field(..., description="Index of the chunk within the document.")
    question: str = Field(..., description="The original question associated with the document.")
    answer: str = Field(..., description="The gold standard answer for the question.")
    text: str = Field(..., description="The chunk text context.")


class RetrievalResponse(BaseModel):
    """
    Response model for semantic retrieval.
    """

    query: str = Field(..., description="The original user query.")
    total_results: int = Field(..., description="Total number of retrieved chunks.")
    results: list[RetrievedChunk] = Field(..., description="List of matched chunks.")