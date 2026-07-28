"""
Veridict Batch Rate Controller.

Regulates batch execution and Gemini API request throughput.
"""

import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class BatchRateController:
    """Lightweight concurrency and rate limiter for Gemini API batch execution."""

    def __init__(self, max_concurrency: int = 1, inter_batch_delay: float = 0.5) -> None:
        self.max_concurrency = max_concurrency
        self.inter_batch_delay = inter_batch_delay
        self._semaphore = asyncio.Semaphore(max_concurrency)

    def acquire_slot_sync(self) -> None:
        """Synchronous inter-batch throttling delay."""
        if self.inter_batch_delay > 0:
            time.sleep(self.inter_batch_delay)

    async def execute_rate_limited(self, func, *args, **kwargs):
        """Execute async function within semaphore bounds."""
        async with self._semaphore:
            if self.inter_batch_delay > 0:
                await asyncio.sleep(self.inter_batch_delay)
            return await func(*args, **kwargs)
