"""
Veridict Batch Input Parsers (CSV & Digital QA PDF).

Parses CSV files and digitally typed searchable PDFs into standardized
BatchQAPairInput objects. Rejects scanned PDFs and files exceeding 30 rows.
"""

import csv
import io
import re
from typing import Any, Sequence
from pypdf import PdfReader

from app.core.config import settings
from app.schemas.batch_evaluation import BatchQAPairInput
from app.services.batch_parser_base import BaseBatchParser, BatchParserFactory


class CSVBatchParser(BaseBatchParser):
    """Parses CSV upload files up to MAX_BATCH_ROWS into normalized BatchQAPairInputs."""

    @classmethod
    def parse(cls, content: bytes) -> list[BatchQAPairInput]:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        file_obj = io.StringIO(text)
        reader = csv.DictReader(file_obj)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or corrupted.")

        field_map = cls._normalize_headers(list(reader.fieldnames))

        items: list[BatchQAPairInput] = []
        for idx, row in enumerate(reader, start=1):
            item = cls._process_row(idx, row, field_map)
            if item:
                items.append(item)

        if not items:
            raise ValueError("CSV file contains no valid QA data rows.")

        if len(items) > settings.MAX_BATCH_ROWS:
            raise ValueError(
                f"Batch limit exceeded. Maximum allowed is {settings.MAX_BATCH_ROWS} QA pairs (found {len(items)} rows)."
            )

        return items

    @staticmethod
    def _classify_header(clean: str) -> str | None:
        ref_keys = ("reference", "ground truth", "groundtruth", "golden", "expected", "ref answer")
        if clean == "ref" or any(k in clean for k in ref_keys):
            return "reference_answer"

        q_keys = ("question", "prompt", "query", "input", "instruction")
        if clean == "q" or any(k in clean for k in q_keys):
            return "question"

        a_keys = ("ai response", "response", "answer", "output", "completion", "generation", "prediction", "model output", "ai output")
        if clean == "a" or any(k in clean for k in a_keys):
            return "ai_response"

        return None

    @classmethod
    def _normalize_headers(cls, fieldnames: Sequence[str]) -> dict[str, str]:
        field_map: dict[str, str] = {}
        for field in fieldnames:
            clean = re.sub(r"[\s_\-]+", " ", field.strip().lower())
            category = cls._classify_header(clean)
            if category and category not in field_map:
                field_map[category] = field

        if "question" not in field_map or "ai_response" not in field_map:
            raise ValueError(
                "CSV must contain 'Question' and 'AI Response' columns. "
                "Found columns: " + ", ".join(fieldnames)
            )

        return field_map

    @staticmethod
    def _process_row(idx: int, row: dict[str, Any], field_map: dict[str, str]) -> BatchQAPairInput | None:
        q_val = (row.get(field_map["question"]) or "").strip()
        a_val = (row.get(field_map["ai_response"]) or "").strip()
        ref_col = field_map.get("reference_answer")
        ref_val = (row.get(ref_col) or "").strip() if ref_col else None

        if not q_val and not a_val:
            return None  # Skip blank rows

        if not q_val:
            raise ValueError(f"Row {idx}: Question cannot be empty.")
        if not a_val:
            raise ValueError(f"Row {idx}: AI Response cannot be empty.")

        return BatchQAPairInput(
            id=f"QA-{idx:02d}",
            row_index=idx,
            question=q_val,
            ai_response=a_val,
            reference_answer=ref_val if ref_val else None,
        )


class PDFBatchParser(BaseBatchParser):
    """Parses digital, searchable QA PDFs into normalized BatchQAPairInputs."""

    @classmethod
    def parse(cls, content: bytes) -> list[BatchQAPairInput]:
        file_obj = io.BytesIO(content)
        full_text = cls._extract_pdf_text(file_obj)

        if len(full_text.strip()) < 20:
            raise ValueError(
                "Scanned or image-based PDFs are not supported. "
                "Please upload a digital, searchable QA PDF."
            )

        items = cls._parse_regex_matches(full_text)
        if not items:
            items = cls._parse_line_by_line(full_text)

        if not items:
            raise ValueError(
                "Could not detect structured QA blocks in the PDF. "
                "Ensure questions and responses use clear labels (e.g. 'Question:' and 'AI Response:')."
            )

        if len(items) > settings.MAX_BATCH_ROWS:
            raise ValueError(
                f"Batch limit exceeded. Maximum allowed is {settings.MAX_BATCH_ROWS} QA pairs (found {len(items)} rows)."
            )

        return items

    @staticmethod
    def _extract_pdf_text(file_obj: io.BytesIO) -> str:
        try:
            reader = PdfReader(file_obj)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

        full_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"
        return full_text

    @staticmethod
    def _parse_regex_matches(full_text: str) -> list[BatchQAPairInput]:
        pattern = re.compile(
            r"(?:Question|Q\d*|Prompt)\s*:\s*(.*?)\n\s*"
            r"(?:AI Response|Response|Answer|A)\s*:\s*(.*?)\n\s*"
            r"(?:(?:Reference Answer|Reference|Ref)\s*:\s*(.*?)\n\s*)?"
            r"(?=(?:Question|Q\d*|Prompt)\s*:|\Z)",
            re.DOTALL | re.IGNORECASE,
        )
        matches = pattern.findall(full_text)
        items: list[BatchQAPairInput] = []

        if matches:
            for idx, match in enumerate(matches, start=1):
                q_text = match[0].strip()
                a_text = match[1].strip()
                ref_text = match[2].strip() if len(match) > 2 and match[2] else None

                if q_text and a_text:
                    items.append(
                        BatchQAPairInput(
                            id=f"QA-{idx:02d}",
                            row_index=idx,
                            question=q_text,
                            ai_response=a_text,
                            reference_answer=ref_text if ref_text else None,
                        )
                    )
        return items

    @staticmethod
    def _parse_line_tag(line_str: str) -> tuple[str | None, str]:
        if ":" not in line_str:
            return None, line_str
        parts = line_str.split(":", 1)
        prefix = parts[0].strip().lower()
        val = parts[1].strip()
        if prefix in ["question", "prompt", "q"] or (prefix.startswith("q") and prefix[1:].isdigit()):
            return "Q", val
        if prefix in ["ai response", "response", "answer", "a"]:
            return "A", val
        if prefix in ["reference answer", "reference", "ref", "ground truth"]:
            return "REF", val
        return None, line_str

    @staticmethod
    def _flush_item(idx: int, q: str, a: str, ref: str) -> BatchQAPairInput | None:
        if q and a:
            return BatchQAPairInput(
                id=f"QA-{idx:02d}",
                row_index=idx,
                question=q,
                ai_response=a,
                reference_answer=ref if ref else None,
            )
        return None

    @staticmethod
    def _parse_line_by_line(full_text: str) -> list[BatchQAPairInput]:
        items: list[BatchQAPairInput] = []
        current_q, current_a, current_ref = "", "", ""
        idx = 1

        for line in full_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            tag, val = PDFBatchParser._parse_line_tag(line_str)
            if tag == "Q":
                flushed = PDFBatchParser._flush_item(idx, current_q, current_a, current_ref)
                if flushed:
                    items.append(flushed)
                    idx += 1
                    current_q, current_a, current_ref = "", "", ""
                current_q = val
            elif tag == "A":
                current_a = val
            elif tag == "REF":
                current_ref = val
            elif current_a:
                current_a += " " + line_str
            elif current_q:
                current_q += " " + line_str

        final_item = PDFBatchParser._flush_item(idx, current_q, current_a, current_ref)
        if final_item:
            items.append(final_item)

        return items


# Register concrete parsers with factory
BatchParserFactory.register("CSV", CSVBatchParser)
BatchParserFactory.register("PDF", PDFBatchParser)
