"""
Shared schemas for the Judge LLM infrastructure.

Provides a generic typed result container that all future Judge Agents
(Relevance, Accuracy, Hallucination, etc.) will use to receive validated
structured output along with model-used metadata.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class JudgeLLMResult(BaseModel, Generic[T]):
    """
    Generic container for a validated Judge LLM response.

    Attributes:
        result: The validated Pydantic model instance returned by the LLM.
        model_used: The Gemini model name that produced the final response.
    """

    result: T = Field(
        ...,
        description="Validated structured output from the Judge LLM."
    )

    model_used: str = Field(
        ...,
        description="Gemini model that produced this result."
    )


class RelevanceJudgeOutput(BaseModel):
    """
    Structured output schema for the Relevance Judge Agent.
    """

    relevance_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="The relevance score of the response from 1 (irrelevant) to 5 (highly relevant)."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="A concise explanation justifying the assigned score."
    )


class AccuracyJudgeOutput(BaseModel):
    """
    Structured output schema for the Accuracy Judge Agent.
    """

    accuracy_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="The accuracy score of the response from 1 (factually incorrect) to 5 (completely accurate)."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="A concise explanation detailing which factual claims were supported or contradicted by the evidence."
    )

