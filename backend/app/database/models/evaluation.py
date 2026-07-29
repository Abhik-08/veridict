"""
Evaluation Model: Stores complete, structured evaluation history items.
"""
from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, GUID

JSON_TYPE = JSONB().with_variant(JSON(), "sqlite")


class Evaluation(BaseModel):
    """
    Evaluation Model: Stores complete, structured evaluation history items.
    Stores full evaluation_result JSON payload to isolate future judge agent schema changes.
    """

    __tablename__ = "evaluations"

    user_id = Column(GUID, ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=True)

    retrieved_evidence = Column(JSON_TYPE, nullable=True)
    evaluation_result = Column(JSON_TYPE, nullable=True)

    overall_score = Column(Float, nullable=True, index=True)
    confidence = Column(Float, nullable=True)
    verdict = Column(String(50), nullable=True, index=True)
    reasoning = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False, default="SINGLE", index=True)

    batch_job_id = Column(GUID, ForeignKey("batch_jobs.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relationships
    user = relationship("Profile", back_populates="evaluations")
    batch_job = relationship("BatchJob", back_populates="evaluations")
