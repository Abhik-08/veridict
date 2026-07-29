from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class BatchResult(BaseModel):
    """
    BatchResult Model: Stores item-level evaluation results within a batch job.
    """

    __tablename__ = "batch_results"

    batch_job_id = Column(UUID(as_uuid=True), ForeignKey("batch_jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=True, index=True)
    verdict = Column(String(50), nullable=True, index=True)
    reasoning = Column(Text, nullable=True)

    # Relationships
    batch_job = relationship("BatchJob", back_populates="results")
