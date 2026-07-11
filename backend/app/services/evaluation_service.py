from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse
)
from app.schemas.retrieval import RetrievedChunk
from app.services.retrieval_service import RetrievalService


class EvaluationService:
    """
    Service responsible for preparing the evaluation payload.

    This service retrieves relevant knowledge chunks based on
    the user's question and combines them with the submitted
    inputs. AI evaluation will be added in future phases.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()

    def evaluate(
        self,
        request: EvaluationRequest
    ) -> EvaluationResponse:
        """
        Prepare the evaluation payload.

        Args:
            request: Evaluation request.

        Returns:
            EvaluationResponse containing the submitted
            inputs and retrieved knowledge chunks.
        """

        retrieval_results = self.retrieval_service.retrieve(
            request.question
        )

        retrieved_chunks = [
            RetrievedChunk(**chunk)
            for chunk in retrieval_results
        ]

        return EvaluationResponse(
            question=request.question,
            ai_response=request.ai_response,
            reference_answer=request.reference_answer,
            retrieved_chunks=retrieved_chunks
        )