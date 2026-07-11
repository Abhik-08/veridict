import hashlib
import json
import os
from datetime import datetime, timezone
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFCacheService:
    """
    Service responsible for managing SHA256 PDF document fingerprinting and caching.
    Avoids redundant processing, embedding generation, and Pinecone uploads.
    """

    def __init__(self) -> None:
        self.cache_file = settings.PDF_CACHE_FILE
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache entries from the configured JSON file."""
        if not settings.CACHE_ENABLED:
            self.cache = {}
            return

        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load PDF cache file: {e}")
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self) -> None:
        """Persist cache entries to the JSON file."""
        if not settings.CACHE_ENABLED:
            return

        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save PDF cache file: {e}")

    @staticmethod
    def compute_hash(content: bytes) -> str:
        """Compute the SHA256 hash/fingerprint of PDF content bytes."""
        return hashlib.sha256(content).hexdigest()

    def get_cached_namespace(self, file_hash: str) -> dict | None:
        """
        Check if the document is already cached.

        Args:
            file_hash (str): SHA256 of the PDF content.

        Returns:
            dict | None: Cached entry details if hit, else None.
        """
        if not settings.CACHE_ENABLED:
            return None

        # Reload cache to stay synchronized in case of multi-task updates
        self._load_cache()
        entry = self.cache.get(file_hash)
        if entry:
            logger.info(f"PDF cache HIT for hash: {file_hash} -> namespace: {entry['namespace']}")
            return entry
        return None

    def cache_namespace(
        self,
        file_hash: str,
        namespace: str,
        filename: str,
        pages: int,
        character_count: int
    ) -> dict:
        """
        Store a new ingestion record in the cache.

        Args:
            file_hash: SHA256 of the PDF content.
            namespace: Ingested Pinecone namespace.
            filename: PDF filename.
            pages: Total pages.
            character_count: Total characters.

        Returns:
            dict: The newly created cache entry.
        """
        entry = {
            "hash": file_hash,
            "namespace": namespace,
            "filename": filename,
            "pages": pages,
            "character_count": character_count,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if settings.CACHE_ENABLED:
            self._load_cache()
            self.cache[file_hash] = entry
            self._save_cache()
            logger.info(f"Cached namespace: {namespace} for hash: {file_hash}")

        return entry

    def delete_cache_entry(self, namespace: str) -> None:
        """Remove a namespace cache entry when it expires."""
        if not settings.CACHE_ENABLED:
            return

        self._load_cache()
        hash_to_delete = None
        for file_hash, entry in self.cache.items():
            if entry.get("namespace") == namespace:
                hash_to_delete = file_hash
                break

        if hash_to_delete:
            del self.cache[hash_to_delete]
            self._save_cache()
            logger.info(f"Removed cache entry for namespace: {namespace}")
