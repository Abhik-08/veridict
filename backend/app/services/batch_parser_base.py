"""
Veridict Abstract Batch Parser Base & Factory.

Provides an extensible abstraction for parsing dataset files (CSV, PDF, Excel, JSON)
into normalized BatchQAPairInput objects.
"""

from abc import ABC, abstractmethod
from typing import Type

from app.schemas.batch_evaluation import BatchQAPairInput


class BaseBatchParser(ABC):
    """Abstract Base Class for all Batch Input Parsers."""

    @classmethod
    @abstractmethod
    def parse(cls, content: bytes) -> list[BatchQAPairInput]:
        """
        Parse raw binary file content into standardized BatchQAPairInput objects.

        Args:
            content: Binary content of the uploaded dataset file.

        Returns:
            list[BatchQAPairInput]: Normalized list of QA pairs.
        """
        pass


class BatchParserFactory:
    """Factory for instantiating registered dataset parsers."""

    _registry: dict[str, Type[BaseBatchParser]] = {}

    @classmethod
    def register(cls, file_type: str, parser_cls: Type[BaseBatchParser]) -> None:
        cls._registry[file_type.upper()] = parser_cls

    @classmethod
    def get_parser(cls, file_type: str) -> BaseBatchParser:
        file_key = file_type.upper()
        if file_key not in cls._registry:
            raise ValueError(f"No parser registered for file type '{file_type}'. Supported: {list(cls._registry.keys())}")
        return cls._registry[file_key]()
