"""
Unit and integration tests for Veridict Batch Evaluation Module.
"""

import pytest
from app.schemas.batch_evaluation import (
    BatchItemEvaluationResult,
    BatchProgress,
    BatchQAPairInput,
)
from app.services.batch_evaluation_service import BatchEvaluationService
from app.services.batch_parsers import CSVBatchParser, PDFBatchParser
from app.services.batch_report_generator import BatchReportGenerator


class TestCSVBatchParser:
    def test_parse_valid_csv(self):
        csv_data = (
            "Question,AI Response,Reference Answer\n"
            "What is Python?,Python is a programming language.,Python is a high-level programming language.\n"
            "What is FastAPI?,FastAPI is a web framework.,FastAPI is a Python web framework.\n"
        ).encode("utf-8")

        items = CSVBatchParser.parse(csv_data)
        assert len(items) == 2
        assert items[0].id == "QA-01"
        assert items[0].question == "What is Python?"
        assert items[0].ai_response == "Python is a programming language."
        assert items[0].reference_answer == "Python is a high-level programming language."
        assert items[1].id == "QA-02"

    def test_parse_missing_required_columns(self):
        csv_data = "ID,Notes,Category\n1,Hello,General\n".encode("utf-8")
        with pytest.raises(ValueError, match="CSV must contain 'Question' and 'AI Response' columns"):
            CSVBatchParser.parse(csv_data)

    def test_parse_csv_with_extra_and_custom_columns(self):
        csv_data = (
            "ID,User Question,Model Output,Expected Answer,Category,Notes\n"
            "1,What is AI?,AI is artificial intelligence.,AI is machine intelligence.,Tech,Important\n"
        ).encode("utf-8")

        items = CSVBatchParser.parse(csv_data)
        assert len(items) == 1
        assert items[0].question == "What is AI?"
        assert items[0].ai_response == "AI is artificial intelligence."
        assert items[0].reference_answer == "AI is machine intelligence."

    def test_parse_exceeding_max_rows(self):
        lines = ["Question,AI Response"]
        for i in range(35):
            lines.append(f"Question {i},Response {i}")
        csv_data = "\n".join(lines).encode("utf-8")

        with pytest.raises(ValueError, match="Batch limit exceeded"):
            CSVBatchParser.parse(csv_data)


class TestPDFBatchParser:
    def test_parse_scanned_pdf_rejection(self):
        pdf_bytes = b"%PDF-1.4 empty pdf text"
        with pytest.raises(ValueError, match="(Invalid or corrupted PDF file|Scanned or image-based PDFs are not supported)"):
            PDFBatchParser.parse(pdf_bytes)


class TestBatchEvaluationService:
    def test_python_verdict_calculation(self):
        service = BatchEvaluationService()
        item_data = {
            "id": "QA-01",
            "row_index": 1,
            "question": "What is Python?",
            "ai_response": "Python is a language.",
            "reference_answer": "Python is a programming language.",
            "evidence_source": "REFERENCE_ANSWER",
        }
        res_data = {
            "relevance_score": 5.0,
            "accuracy_score": 5.0,
            "hallucination_score": 5.0,
            "completeness_score": 5.0,
            "confidence": 0.95,
            "reasoning": "Excellent quality response.",
        }

        result = service._calculate_python_verdict(item_data, res_data)
        assert result.overall_score == 5.0
        assert result.verdict == "PASS"
        assert result.status == "COMPLETED"

    def test_verdict_needs_improvement_threshold(self):
        service = BatchEvaluationService()
        item_data = {
            "id": "QA-02",
            "row_index": 2,
            "question": "What is FastAPI?",
            "ai_response": "FastAPI is a framework.",
        }
        res_data = {
            "relevance_score": 4.0,
            "accuracy_score": 4.0,
            "hallucination_score": 3.0,
            "completeness_score": 3.0,
            "confidence": 0.85,
            "reasoning": "Acceptable but incomplete.",
        }

        result = service._calculate_python_verdict(item_data, res_data)
        assert 3.50 <= result.overall_score < 4.50
        assert result.verdict == "NEEDS_IMPROVEMENT"

    def test_verdict_fail_threshold(self):
        service = BatchEvaluationService()
        item_data = {
            "id": "QA-03",
            "row_index": 3,
            "question": "What is Docker?",
            "ai_response": "Docker is a fruit.",
        }
        res_data = {
            "relevance_score": 1.0,
            "accuracy_score": 1.0,
            "hallucination_score": 1.0,
            "completeness_score": 1.0,
            "confidence": 0.99,
            "reasoning": "Factual hallucination.",
        }

        result = service._calculate_python_verdict(item_data, res_data)
        assert result.overall_score < 3.50
        assert result.verdict == "FAIL"

    def test_job_creation_and_progress_tracking(self):
        service = BatchEvaluationService()
        inputs = [
            BatchQAPairInput(id="QA-01", row_index=1, question="Q1", ai_response="A1"),
            BatchQAPairInput(id="QA-02", row_index=2, question="Q2", ai_response="A2"),
            BatchQAPairInput(id="QA-03", row_index=3, question="Q3", ai_response="A3"),
            BatchQAPairInput(id="QA-04", row_index=4, question="Q4", ai_response="A4"),
        ]

        job = service.create_job(filename="test.csv", file_type="CSV", items=inputs)
        assert job.total_rows == 4
        assert job.total_batches == 2  # ceil(4 / 3) = 2
        assert service.get_progress(job.batch_id) is not None


class TestBatchReportGenerator:
    def test_generate_batch_csv(self):
        items = [
            BatchItemEvaluationResult(
                id="QA-01",
                row_index=1,
                question="What is Python?",
                ai_response="Language",
                reference_answer="Prog Language",
                evidence_source="REFERENCE_ANSWER",
                relevance_score=5.0,
                accuracy_score=5.0,
                hallucination_score=5.0,
                completeness_score=5.0,
                confidence=0.95,
                overall_score=5.0,
                verdict="PASS",
                reasoning="Great",
            )
        ]

        csv_bytes = BatchReportGenerator.generate_batch_csv(items)
        csv_str = csv_bytes.decode("utf-8-sig")
        assert "ID,Row Index,Question" in csv_str
        assert "QA-01,1,What is Python?" in csv_str
        assert "PASS" in csv_str

    def test_generate_batch_pdf(self):
        progress = BatchProgress(
            batch_id="BATCH-TEST01",
            filename="test_dataset.csv",
            file_type="CSV",
            total_rows=1,
            processed_rows=1,
            remaining_rows=0,
            current_batch=1,
            total_batches=1,
            completed_count=1,
            failed_count=0,
            status="COMPLETED",
            items=[
                BatchItemEvaluationResult(
                    id="QA-01",
                    row_index=1,
                    question="What is Python?",
                    ai_response="Language",
                    relevance_score=5.0,
                    accuracy_score=5.0,
                    completeness_score=5.0,
                    overall_score=5.0,
                    verdict="PASS",
                    reasoning="Great",
                )
            ],
        )

        pdf_bytes = BatchReportGenerator.generate_batch_pdf(progress)
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF-")
