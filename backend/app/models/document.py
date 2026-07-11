from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Standard document model used throughout the
    Veridict knowledge pipeline.

    Every knowledge source (datasets, PDFs, future
    connectors) should be represented using this
    unified model.
    """

    document_id: str = Field(
        ...,
        description="Unique identifier for the document."
    )

    source: str = Field(
        ...,
        description="Origin of the document."
    )

    text: str = Field(
        ...,
        description="Document content."
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Additional document metadata."
    )