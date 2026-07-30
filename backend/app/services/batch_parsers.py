"""
Veridict Batch Input Parsers (CSV & Digital QA PDF).

Parses CSV files and digitally typed searchable PDFs into standardized
BatchQAPairInput objects. Rejects scanned PDFs and files exceeding 30 rows.
"""

import csv
import io
import re
import logging
from typing import Any, Sequence
from pypdf import PdfReader

logger = logging.getLogger(__name__)

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
    """
    Parses digital, searchable QA PDFs into normalized BatchQAPairInputs.
    Supports multi-format block extraction, markdown headers, table structures,
    multi-page spanning, normalization, and detailed skip reporting.
    """

    Q_LABEL_KEYWORDS = {
        "question", "q", "prompt", "user question", "query", "input", "instruction"
    }
    A_LABEL_KEYWORDS = {
        "ai response", "response", "answer", "ai answer", "generated response",
        "model response", "output", "completion", "prediction", "ai output", "a"
    }
    REF_LABEL_KEYWORDS = {
        "reference answer", "reference", "expected answer", "ground truth",
        "correct answer", "ref", "ref answer", "golden"
    }

    HEADER_LABEL_REGEX = re.compile(
        r"^(?:"
        r"(?:\#\#\s*|\d+[\.\)]\s*)?"
        r"(\bQUESTION\b|\bQ\b|\bPROMPT\b|\bUSER QUESTION\b|\bQUERY\b|\bINPUT\b|\bINSTRUCTION\b|"
        r"\bAI RESPONSE\b|\bRESPONSE\b|\bANSWER\b|\bAI ANSWER\b|\bGENERATED RESPONSE\b|\bMODEL RESPONSE\b|\bOUTPUT\b|\bCOMPLETION\b|\bPREDICTION\b|\bAI OUTPUT\b|\bA\b|"
        r"\bREFERENCE ANSWER\b|\bREFERENCE\b|\bEXPECTED ANSWER\b|\bGROUND TRUTH\b|\bCORRECT ANSWER\b|\bREF\b|\bREF ANSWER\b|\bGOLDEN\b)"
        r"(?:\s*\d+)?"
        r"\s*:?\s*"
        r"(.*)"
        r")$",
        re.IGNORECASE,
    )

    @classmethod
    def parse(cls, content: bytes) -> list[BatchQAPairInput]:
        file_obj = io.BytesIO(content)
        raw_pages_plain, raw_pages_layout = cls._extract_pdf_pages(file_obj)
        full_text_plain = "\n\n".join(raw_pages_plain).strip()
        full_text_layout = "\n\n".join(raw_pages_layout).strip()

        if len(full_text_plain) < 20 and len(full_text_layout) < 20:
            logger.debug("PDF text length < 20 characters. Rejecting as scanned or empty.")
            raise ValueError(
                "Scanned or image-based PDFs are not supported. "
                "Please upload a digital, searchable QA PDF."
            )

        norm_plain = cls._normalize_text(full_text_plain)

        # Pipeline Stage 1: Table Detection & Parsing (using raw layout text to preserve column spacing)
        table_items = cls._try_parse_table(full_text_layout) or cls._try_parse_table(full_text_plain)
        if table_items:
            logger.debug(f"Detected table layout. Successfully parsed {len(table_items)} QA pairs.")
            if len(table_items) > settings.MAX_BATCH_ROWS:
                raise ValueError(
                    f"Batch limit exceeded. Maximum allowed is {settings.MAX_BATCH_ROWS} QA pairs (found {len(table_items)} rows)."
                )
            return table_items

        # Pipeline Stage 2: Staged Block Parsing
        items, skipped_count, skip_reasons = cls._parse_staged_blocks(norm_plain)

        # Fallback to regex matches if staged block parsing found nothing
        if not items:
            logger.debug("Staged block parser found 0 items. Trying legacy regex match fallback.")
            items = cls._parse_regex_matches(norm_plain)
            if items:
                skipped_count = 0
                skip_reasons = []

        if not items:
            err_msg = "Could not detect structured QA blocks in the PDF."
            if skip_reasons:
                err_msg += f" Skipped {skipped_count} blocks. Reasons:\n" + "\n".join(skip_reasons)
            else:
                err_msg += " Ensure questions and responses use clear labels (e.g. 'Question:' and 'AI Response:')."
            logger.debug(f"Parsing failed: {err_msg}")
            raise ValueError(err_msg)

        if len(items) > settings.MAX_BATCH_ROWS:
            raise ValueError(
                f"Batch limit exceeded. Maximum allowed is {settings.MAX_BATCH_ROWS} QA pairs (found {len(items)} rows)."
            )

        logger.debug(f"Parsed {len(items)} QA pairs successfully. Skipped {skipped_count} blocks.")
        return items

    @staticmethod
    def _extract_pdf_pages(file_obj: io.BytesIO) -> tuple[list[str], list[str]]:
        try:
            reader = PdfReader(file_obj)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

        pages_plain: list[str] = []
        pages_layout: list[str] = []

        for page in reader.pages:
            t_plain = page.extract_text(extraction_mode="plain") or ""
            t_layout = page.extract_text(extraction_mode="layout") or ""
            pages_plain.append(t_plain)
            pages_layout.append(t_layout)

        return pages_plain, pages_layout

    @staticmethod
    def _normalize_text(raw: str) -> str:
        text = raw.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[\u2022\u2023\u25b6\u25c0\u2013\u2014]", "", text)
        lines = []
        for line in text.splitlines():
            cleaned = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(cleaned)
        res = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", res)

    @classmethod
    def _classify_header_token(cls, tag_str: str) -> str | None:
        t = tag_str.lower().strip()
        if t in cls.Q_LABEL_KEYWORDS:
            return "Q"
        if t in cls.A_LABEL_KEYWORDS:
            return "A"
        if t in cls.REF_LABEL_KEYWORDS:
            return "REF"
        return None

    @classmethod
    def _find_table_header(cls, lines: list[str]) -> tuple[int, list[tuple[str, int, int | None]]]:
        pattern = re.compile(
            r"\b(Question|Q|Prompt|User Question|AI Response|Response|Answer|AI Answer|Generated Response|Model Response|Reference Answer|Reference|Expected Answer|Ground Truth|Correct Answer|Ref)\b",
            re.IGNORECASE,
        )
        for idx, line in enumerate(lines[:10]):
            matches = list(pattern.finditer(line))
            if len(matches) < 2:
                continue

            spans = []
            for i, m in enumerate(matches):
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else None
                c_tag = cls._classify_header_token(m.group(1))
                if c_tag:
                    spans.append((c_tag, start, end))

            if any(s[0] == "Q" for s in spans) and any(s[0] == "A" for s in spans):
                return idx, spans

        return -1, []

    @classmethod
    def _try_parse_table(cls, text: str) -> list[BatchQAPairInput] | None:
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return None

        header_idx, col_spans = cls._find_table_header(lines)
        if header_idx == -1 or not col_spans:
            return None

        logger.debug(f"Detected table header at line {header_idx}: {lines[header_idx]}")
        items: list[BatchQAPairInput] = []
        for line in lines[header_idx + 1:]:
            row_dict: dict[str, str] = {}
            for tag, start, end in col_spans:
                cell = line[start:end].strip() if end is not None else line[start:].strip()
                row_dict[tag] = cell

            q_val = row_dict.get("Q", "").strip()
            a_val = row_dict.get("A", "").strip()
            ref_val = row_dict.get("REF", "").strip() or None

            if q_val and a_val:
                item_idx = len(items) + 1
                items.append(
                    BatchQAPairInput(
                        id=f"QA-{item_idx:02d}",
                        row_index=item_idx,
                        question=q_val,
                        ai_response=a_val,
                        reference_answer=ref_val,
                    )
                )

        return items if items else None

    @classmethod
    def _should_flush_block(cls, c_tag: str, current_block: dict[str, list[str]]) -> bool:
        if not current_block:
            return False
        if c_tag == "Q" and ("Q" in current_block or "A" in current_block):
            return True
        if c_tag == "A" and "A" in current_block:
            return True
        return False

    @classmethod
    def _is_numbered_line(cls, stripped: str) -> bool:
        return bool(re.match(r"^\d+[\.\)]$", stripped))

    @classmethod
    def _try_parse_header_line(
        cls, stripped: str, current_block: dict[str, list[str]]
    ) -> tuple[bool, str | None, list[str]]:
        m = cls.HEADER_LABEL_REGEX.match(stripped)
        if not m:
            return False, None, []

        raw_tag, inline_val = m.group(1), m.group(2)
        c_tag = cls._classify_header_token(raw_tag)
        if not c_tag:
            return False, None, []

        inline_list = [inline_val] if inline_val else []
        return True, c_tag, inline_list

    @classmethod
    def _process_block_line(
        cls,
        stripped: str,
        current_block: dict[str, list[str]],
        current_key: str | None,
        raw_blocks: list[dict[str, list[str]]],
    ) -> tuple[dict[str, list[str]], str | None]:
        if cls._is_numbered_line(stripped):
            if current_block and ("Q" in current_block or "A" in current_block):
                raw_blocks.append(current_block)
                return {}, None
            return current_block, current_key

        is_header, c_tag, inline_list = cls._try_parse_header_line(stripped, current_block)
        if is_header and c_tag is not None:
            if cls._should_flush_block(c_tag, current_block):
                raw_blocks.append(current_block)
                current_block = {}
            current_block[c_tag] = inline_list
            return current_block, c_tag

        if current_key and current_key in current_block:
            current_block[current_key].append(stripped)

        return current_block, current_key

    @classmethod
    def _extract_raw_blocks(cls, lines: list[str]) -> list[dict[str, list[str]]]:
        raw_blocks: list[dict[str, list[str]]] = []
        current_block: dict[str, list[str]] = {}
        current_key: str | None = None

        for line in lines:
            stripped = line.strip()
            if stripped:
                current_block, current_key = cls._process_block_line(
                    stripped, current_block, current_key, raw_blocks
                )

        if current_block:
            raw_blocks.append(current_block)

        return raw_blocks

    @classmethod
    def _parse_staged_blocks(cls, norm_text: str) -> tuple[list[BatchQAPairInput], int, list[str]]:
        raw_blocks = cls._extract_raw_blocks(norm_text.splitlines())
        items: list[BatchQAPairInput] = []
        skipped_count = 0
        skip_reasons: list[str] = []

        for b_idx, b in enumerate(raw_blocks, start=1):
            q_str = " ".join(b.get("Q", [])).strip()
            a_str = " ".join(b.get("A", [])).strip()
            ref_str = " ".join(b.get("REF", [])).strip() or None

            if not q_str and not a_str:
                skipped_count += 1
                skip_reasons.append(f"Block {b_idx}: Missing Question and AI Response")
                logger.debug(f"Skipped block {b_idx} because Question and AI Response are missing.")
                continue

            if not q_str:
                skipped_count += 1
                skip_reasons.append(f"Block {b_idx}: Missing Question")
                logger.debug(f"Skipped block {b_idx} because Question is missing.")
                continue

            if not a_str:
                skipped_count += 1
                skip_reasons.append(f"Block {b_idx}: Missing AI Response")
                logger.debug(f"Skipped block {b_idx} because AI Response is missing.")
                continue

            item_idx = len(items) + 1
            items.append(
                BatchQAPairInput(
                    id=f"QA-{item_idx:02d}",
                    row_index=item_idx,
                    question=q_str,
                    ai_response=a_str,
                    reference_answer=ref_str,
                )
            )
            logger.debug(f"Parsed QA block {item_idx}.")

        return items, skipped_count, skip_reasons

    @staticmethod
    def _parse_regex_matches(full_text: str) -> list[BatchQAPairInput]:
        pattern = re.compile(
            r"(?:Question|Q\d*|Prompt|User Question)\s*:\s*(.*?)\n\s*"
            r"(?:AI Response|Response|Answer|A|AI Answer|Model Response)\s*:\s*(.*?)\n\s*"
            r"(?:(?:Reference Answer|Reference|Ref|Expected Answer|Ground Truth)\s*:\s*(.*?)\n\s*)?"
            r"(?=(?:Question|Q\d*|Prompt|User Question)\s*:|\Z)",
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


# Register concrete parsers with factory
BatchParserFactory.register("CSV", CSVBatchParser)
BatchParserFactory.register("PDF", PDFBatchParser)
