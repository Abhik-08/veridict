"""
Shared schemas for the Judge LLM infrastructure.

Provides a generic typed result container that all future Judge Agents
(Relevance, Accuracy, Hallucination, etc.) will use to receive validated
structured output along with model-used metadata.
"""

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field, model_validator

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


class HallucinationJudgeOutput(BaseModel):
    """
    Structured output schema for the Hallucination Judge Agent.

    Supports two statuses:
    - SUCCESS: grounding was evaluated; hallucination_score is 1–5.
    - INSUFFICIENT_EVIDENCE: no usable evidence to evaluate grounding;
      hallucination_score is null.
    """

    status: Literal["SUCCESS", "INSUFFICIENT_EVIDENCE"] = Field(
        ...,
        description=(
            "Evaluation outcome status. "
            "'SUCCESS' when grounding could be evaluated, "
            "'INSUFFICIENT_EVIDENCE' when no usable evidence was available."
        ),
    )

    hallucination_score: int | None = Field(
        default=None,
        description=(
            "The hallucination score of the response from 1 (ungrounded/fabricated) "
            "to 5 (completely grounded). Null when status is INSUFFICIENT_EVIDENCE."
        ),
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="A concise explanation detailing which factual claims were supported or ungrounded by the evidence."
    )

    @model_validator(mode="after")
    def _validate_score_status_consistency(self) -> "HallucinationJudgeOutput":
        """Enforce that SUCCESS requires a score in [1,5] and INSUFFICIENT_EVIDENCE requires null."""
        if self.status == "SUCCESS":
            if self.hallucination_score is None:
                raise ValueError(
                    "hallucination_score must be provided (1–5) when status is SUCCESS."
                )
            if not (1 <= self.hallucination_score <= 5):
                raise ValueError(
                    f"hallucination_score must be between 1 and 5, got {self.hallucination_score}."
                )
        elif self.status == "INSUFFICIENT_EVIDENCE":
            if self.hallucination_score is not None:
                raise ValueError(
                    "hallucination_score must be null when status is INSUFFICIENT_EVIDENCE."
                )
        return self


class CompletenessJudgeOutput(BaseModel):
    """
    Structured output schema for the Completeness Judge Agent.
    """

    completeness_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="The completeness score of the response from 1 (incomplete) to 5 (completely covers all requested aspects)."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="A concise explanation detailing which requested aspects were covered or missing."
    )

    covered_aspects: list[str] = Field(
        default_factory=list,
        description="List of specific question aspects/requirements satisfied by the AI response."
    )

    missing_aspects: list[str] = Field(
        default_factory=list,
        description="List of specific question aspects/requirements missed or omitted by the AI response."
    )


class VerdictReasoningOutput(BaseModel):
    """
    Structured LLM output schema for the Verdict Agent reasoning generation.
    """

    reasoning: str = Field(
        ...,
        min_length=1,
        description="A concise summary explanation synthesising the judge scores, calculated overall score, and final verdict."
    )


class VerdictOutput(BaseModel):
    """
    Final aggregated verdict result output model.
    """

    overall_score: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Deterministic weighted average overall quality score (1.00 to 5.00)."
    )

    verdict: Literal["PASS", "NEEDS_IMPROVEMENT", "FAIL"] = Field(
        ...,
        description="Final quality verdict category based on overall score thresholds."
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="Synthesized summary reasoning explaining the verdict."
    )

    weights_used: dict[str, float] = Field(
        ...,
        description="Normalized weights applied to judge scores during weighted average calculation."
    )

    model_used: str = Field(
        ...,
        description="Gemini model that generated the verdict reasoning summary."
    )



