"""
Veridict Abstract Batch Exporter Base & Factory.

Provides an extensible abstraction for exporting batch evaluation results into
various file formats (CSV, PDF, Excel, JSON).
"""

from abc import ABC, abstractmethod
from typing import Type

from app.schemas.batch_evaluation import BatchProgress


class BaseBatchExporter(ABC):
    """Abstract Base Class for all Batch Exporters."""

    @abstractmethod
    def export(self, progress: BatchProgress) -> bytes:
        """
        Export batch progress and item results into binary file format.

        Args:
            progress: BatchProgress job state.

        Returns:
            bytes: Exported file binary data.
        """
        pass


class BatchExporterFactory:
    """Factory for instantiating registered dataset exporters."""

    _registry: dict[str, Type[BaseBatchExporter]] = {}

    @classmethod
    def register(cls, export_type: str, exporter_cls: Type[BaseBatchExporter]) -> None:
        cls._registry[export_type.upper()] = exporter_cls

    @classmethod
    def get_exporter(cls, export_type: str) -> BaseBatchExporter:
        key = export_type.upper()
        if key not in cls._registry:
            raise ValueError(f"No exporter registered for format '{export_type}'. Supported: {list(cls._registry.keys())}")
        return cls._registry[key]()
