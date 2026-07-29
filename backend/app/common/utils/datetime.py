"""
Datetime Utilities for Veridict Common Infrastructure.
Provides timezone-safe UTC datetime helpers and ISO formatting routines.
"""
from datetime import datetime, timezone
from typing import Optional
from app.common.constants import TIMESTAMP_FORMAT


def utcnow() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def format_iso_timestamp(dt: Optional[datetime] = None) -> str:
    """Formats a datetime object as an ISO 8601 UTC timestamp string."""
    target = dt or utcnow()
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    return target.isoformat()


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """Parses an ISO 8601 timestamp string into a datetime object."""
    return datetime.fromisoformat(timestamp_str)
