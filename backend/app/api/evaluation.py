from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile
)

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
async def evaluate_response(
    question: str = Form(...),
    ai_response: str = Form(...),
    reference_answer: str | None = Form(None),
    pdf_file: UploadFile | None = File(None)
):
    """
    Prepare the evaluation payload.

    Accepts:

    - User question
    - AI response
    - Optional reference answer
    - Optional PDF document

    The uploaded PDF (if provided) will be
    processed and used as an additional
    knowledge source during retrieval.
    """

    try:

        request = EvaluationRequest(
            question=question,
            ai_response=ai_response,
            reference_answer=reference_answer
        )

        return await evaluation_service.evaluate(
            request=request,
            pdf_file=pdf_file
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )