from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.models.evaluation import Evaluation


class EvaluationRepository:
    """
    Repository layer for Single Evaluation database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, evaluation_id: UUID) -> Optional[Evaluation]:
        return self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

    def get_by_user_id(self, user_id: UUID, limit: int = 50) -> List[Evaluation]:
        return (
            self.db.query(Evaluation)
            .filter(Evaluation.user_id == user_id)
            .order_by(Evaluation.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, **kwargs) -> Evaluation:
        evaluation = Evaluation(**kwargs)
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation
