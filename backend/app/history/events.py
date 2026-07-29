"""
History Domain Events Module for Veridict.
Provides a decoupled event notification dispatch system for evaluation lifecycle events.
Emits structured production logs and serves as an extension point for activity feeds, analytics, and metrics.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class HistoryEvents:
    """
    Centralized event dispatcher for Evaluation History lifecycle events.
    Contains zero database logic, zero HTTP context, and zero side effects.
    """

    _subscribers: List[Callable[[str, Dict[str, Any]], None]] = []

    @classmethod
    def subscribe(cls, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """Registers a custom listener callback for domain event dispatch."""
        if handler not in cls._subscribers:
            cls._subscribers.append(handler)

    @classmethod
    def unsubscribe(cls, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """Unregisters a domain event listener callback."""
        if handler in cls._subscribers:
            cls._subscribers.remove(handler)

    @classmethod
    def _dispatch(cls, event_type: str, payload: Dict[str, Any]) -> None:
        """Internal dispatcher that logs the event and notifies subscribers."""
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Emit concise production log
        user_str = str(payload.get("user_id", "N/A"))
        eval_str = str(payload.get("evaluation_id", "N/A"))
        batch_str = str(payload.get("batch_id", "N/A"))

        if event_type == "evaluation_saved":
            logger.info("Domain Event: Evaluation saved | user=%s | eval_id=%s | score=%s | verdict=%s",
                        user_str, eval_str, payload.get("overall_score"), payload.get("verdict"))
        elif event_type == "evaluation_viewed":
            logger.info("Domain Event: Evaluation viewed | user=%s | eval_id=%s", user_str, eval_str)
        elif event_type == "evaluation_deleted":
            logger.info("Domain Event: Evaluation deleted | user=%s | eval_id=%s", user_str, eval_str)
        elif event_type == "batch_created":
            logger.info("Domain Event: Batch created | user=%s | batch_id=%s | total_items=%s",
                        user_str, batch_str, payload.get("total_items"))
        elif event_type == "batch_viewed":
            logger.info("Domain Event: Batch viewed | user=%s | batch_id=%s", user_str, batch_str)
        elif event_type == "batch_deleted":
            logger.info("Domain Event: Batch deleted | user=%s | batch_id=%s", user_str, batch_str)
        elif event_type == "batch_completed":
            logger.info("Domain Event: Batch completed | user=%s | batch_id=%s | completed=%s/%s",
                        user_str, batch_str, payload.get("completed_items"), payload.get("total_items"))
        elif event_type == "batch_failed":
            logger.warning("Domain Event: Batch failed | user=%s | batch_id=%s | error=%s",
                           user_str, batch_str, payload.get("error"))
        elif event_type == "statistics_requested":
            logger.info("Domain Event: Statistics requested | user=%s", user_str)
        elif event_type == "history_cleanup":
            logger.info("Domain Event: History cleanup | user=%s | deleted_count=%s",
                        user_str, payload.get("deleted_count"))

        # Trigger subscriber callbacks asynchronously or synchronously
        for subscriber in cls._subscribers:
            try:
                subscriber(event_type, payload)
            except Exception as subscriber_err:
                logger.warning("Domain Event subscriber error: %s", subscriber_err)

    @classmethod
    def evaluation_saved(
        cls,
        user_id: UUID,
        evaluation_id: UUID,
        overall_score: float,
        verdict: str,
    ) -> None:
        """Emitted when an evaluation record is successfully saved."""
        cls._dispatch("evaluation_saved", {
            "user_id": user_id,
            "evaluation_id": evaluation_id,
            "overall_score": overall_score,
            "verdict": verdict,
        })

    @classmethod
    def evaluation_viewed(cls, user_id: UUID, evaluation_id: UUID) -> None:
        """Emitted when an evaluation record detail is accessed."""
        cls._dispatch("evaluation_viewed", {"user_id": user_id, "evaluation_id": evaluation_id})

    @classmethod
    def evaluation_deleted(cls, user_id: UUID, evaluation_id: UUID) -> None:
        """Emitted when an evaluation history record is deleted."""
        cls._dispatch("evaluation_deleted", {"user_id": user_id, "evaluation_id": evaluation_id})

    @classmethod
    def batch_created(cls, user_id: UUID, batch_id: UUID, total_items: int, filename: str) -> None:
        """Emitted when a new batch job is initialized."""
        cls._dispatch("batch_created", {
            "user_id": user_id,
            "batch_id": batch_id,
            "total_items": total_items,
            "filename": filename,
        })

    @classmethod
    def batch_viewed(cls, user_id: UUID, batch_id: UUID) -> None:
        """Emitted when a batch job detail is accessed."""
        cls._dispatch("batch_viewed", {"user_id": user_id, "batch_id": batch_id})

    @classmethod
    def batch_deleted(cls, user_id: UUID, batch_id: UUID) -> None:
        """Emitted when a batch job and its evaluations are deleted."""
        cls._dispatch("batch_deleted", {"user_id": user_id, "batch_id": batch_id})

    @classmethod
    def batch_completed(cls, user_id: UUID, batch_id: UUID, completed_items: int, total_items: int) -> None:
        """Emitted when a batch job finishes processing all rows."""
        cls._dispatch("batch_completed", {
            "user_id": user_id,
            "batch_id": batch_id,
            "completed_items": completed_items,
            "total_items": total_items,
        })

    @classmethod
    def batch_failed(cls, user_id: UUID, batch_id: UUID, error: str) -> None:
        """Emitted when a batch job encounters a fatal execution error."""
        cls._dispatch("batch_failed", {
            "user_id": user_id,
            "batch_id": batch_id,
            "error": error,
        })

    @classmethod
    def statistics_requested(cls, user_id: UUID) -> None:
        """Emitted when user dashboard statistics are calculated."""
        cls._dispatch("statistics_requested", {"user_id": user_id})

    @classmethod
    def history_cleanup(cls, user_id: UUID, deleted_count: int) -> None:
        """Emitted when historical evaluations are pruned or cleared."""
        cls._dispatch("history_cleanup", {"user_id": user_id, "deleted_count": deleted_count})
