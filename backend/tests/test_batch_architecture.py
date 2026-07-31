"""
Veridict Batch Evaluation Architecture Unit Tests.

Tests parser abstraction, input validation, prompt builder, response validator,
statistics service, exporter factory, and rate controller.
"""

import pytest
from app.schemas.batch_evaluation import BatchProgress, BatchQAPairInput, BatchItemEvaluationResult
from app.services.batch_parser_base import BaseBatchParser, BatchParserFactory
from app.services.batch_parsers import CSVBatchParser, PDFBatchParser
from app.services.batch_validator import BatchInputValidator
from app.services.batch_prompt_builder import BatchPromptBuilder
from app.services.batch_response_validator import BatchResponseValidator
from app.services.batch_statistics_service import BatchStatisticsService
from app.services.batch_exporter_base import BaseBatchExporter, BatchExporterFactory
from app.services.batch_rate_controller import BatchRateController


class TestBatchParserFactory:
    def test_factory_returns_registered_parsers(self):
        csv_parser = BatchParserFactory.get_parser("CSV")
        pdf_parser = BatchParserFactory.get_parser("PDF")
        assert isinstance(csv_parser, BaseBatchParser)
        assert isinstance(pdf_parser, BaseBatchParser)

    def test_factory_raises_unsupported_type(self):
        with pytest.raises(ValueError, match="No parser registered for file type 'EXCEL'"):
            BatchParserFactory.get_parser("EXCEL")


class TestBatchInputValidator:
    def test_validates_clean_items(self):
        items = [
            BatchQAPairInput(id="QA-01", row_index=1, question="What is RAG?", ai_response="Retrieval Augmented Gen"),
        ]
        validated = BatchInputValidator.validate(items)
        assert len(validated) == 1

    def test_rejects_empty_question(self):
        items = [
            BatchQAPairInput(id="QA-01", row_index=1, question="  ", ai_response="Answer"),
        ]
        with pytest.raises(ValueError, match="Question cannot be empty"):
            BatchInputValidator.validate(items)

    def test_rejects_empty_ai_response(self):
        items = [
            BatchQAPairInput(id="QA-01", row_index=1, question="Question?", ai_response=""),
        ]
        with pytest.raises(ValueError, match="AI Response cannot be empty"):
            BatchInputValidator.validate(items)


class TestBatchPromptBuilder:
    def test_builds_formatted_batch_prompt(self):
        items = [
            {"id": "QA-01", "question": "Q1?", "ai_response": "A1"},
        ]
        prompt = BatchPromptBuilder.build_prompt(items)
        assert "EVALUATION BATCH:" in prompt
        assert "--- ITEM ID: QA-01 ---" in prompt
        assert "QUESTION: Q1?" in prompt
        assert "AI RESPONSE: A1" in prompt


class TestBatchResponseValidator:
    def test_validates_correct_json_response(self):
        raw_json = """
        [
            {
                "id": "QA-01",
                "relevance_score": 5,
                "accuracy_score": 5,
                "hallucination_score": 5,
                "completeness_score": 5,
                "reasoning": "Excellent answer."
            }
        ]
        """
        validated = BatchResponseValidator.validate_and_parse(raw_json)
        assert len(validated) == 1
        assert validated[0]["id"] == "QA-01"
        assert validated[0]["relevance_score"] == 5.0

    def test_rejects_out_of_bounds_score(self):
        raw_json = """
        [
            {
                "id": "QA-01",
                "relevance_score": 10,
                "accuracy_score": 5,
                "completeness_score": 5,
                "reasoning": "Invalid score"
            }
        ]
        """
        with pytest.raises(ValueError, match="relevance_score"):
            BatchResponseValidator.validate_and_parse(raw_json)


class TestBatchStatisticsService:
    def test_calculates_metrics(self):
        items = [
            BatchItemEvaluationResult(
                id="QA-01",
                row_index=1,
                question="Q1",
                ai_response="A1",
                relevance_score=5.0,
                accuracy_score=5.0,
                completeness_score=5.0,
                overall_score=5.0,
                verdict="PASS",
            ),
            BatchItemEvaluationResult(
                id="QA-02",
                row_index=2,
                question="Q2",
                ai_response="A2",
                relevance_score=2.0,
                accuracy_score=2.0,
                completeness_score=2.0,
                overall_score=2.0,
                verdict="FAIL",
            ),
        ]
        stats = BatchStatisticsService.calculate_statistics(items=items, elapsed_seconds=1.5, gemini_calls=1)
        assert stats["total_items"] == 2
        assert stats["pass_count"] == 1
        assert stats["fail_count"] == 1
        assert stats["pass_rate_percent"] == 50.0
        assert stats["avg_overall_score"] == 3.50


class TestBatchExporterFactory:
    def test_factory_returns_csv_and_pdf_exporters(self):
        csv_exp = BatchExporterFactory.get_exporter("CSV")
        pdf_exp = BatchExporterFactory.get_exporter("PDF")
        assert isinstance(csv_exp, BaseBatchExporter)
        assert isinstance(pdf_exp, BaseBatchExporter)


class TestBatchRateController:
    def test_rate_controller_initialization(self):
        controller = BatchRateController(max_concurrency=2, inter_batch_delay=0.1)
        assert controller.max_concurrency == 2
        assert controller.inter_batch_delay == 0.1
