from fastapi import APIRouter, HTTPException

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse
)
from app.services.evaluation_service import EvaluationService

router = APIRouter(
    prefix="/evaluate",
    tags=["AI Response Evaluation"]
)

evaluation_service = EvaluationService()


@router.post(
    "",
    response_model=EvaluationResponse
)
def evaluate_response(
    request: EvaluationRequest
):
    """
    Prepare the evaluation payload.

    This endpoint accepts a user question,
    AI-generated response, and an optional
    reference answer. It retrieves relevant
    knowledge chunks from the knowledge base
    and returns the combined payload.

    AI evaluation will be added in future phases.
    """

    try:
        return evaluation_service.evaluate(request)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )