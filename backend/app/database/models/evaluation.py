from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class Evaluation(BaseModel):
    """
    Evaluation Model: Stores single evaluation pipeline results.
    """

    __tablename__ = "evaluations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=True)
    retrieved_context = Column(Text, nullable=True)

    relevance_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    hallucination_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, index=True)

    verdict = Column(String(50), nullable=True, index=True)
    reasoning = Column(Text, nullable=True)

    # Relationships
    user = relationship("Profile", back_populates="evaluations")
