from fastapi import APIRouter, HTTPException

from app.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunk
)
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/retrieve",
    tags=["Semantic Retrieval"]
)

retrieval_service = RetrievalService()


@router.post(
    "",
    response_model=RetrievalResponse
)
def retrieve_chunks(request: RetrievalRequest) -> RetrievalResponse:
    """
    Retrieve the Top-K most relevant knowledge chunks
    for a given user query.
    """

    try:
        results = retrieval_service.retrieve(request.query)

        retrieved_chunks = [
            RetrievedChunk(
                id=result["id"],
                score=result["score"],
                source=result["source"],
                document_id=result["document_id"],
                chunk_index=result["chunk_index"],
                question=result["question"],
                answer=result["answer"],
                text=result["text"]
            )
            for result in results
        ]

        return RetrievalResponse(
            query=request.query,
            total_results=len(retrieved_chunks),
            results=retrieved_chunks
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )