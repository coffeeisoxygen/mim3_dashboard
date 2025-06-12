"""Shared utilities untuk ORM dan Streamlit connection operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from loguru import logger


class DateTimeUtils:
    """Centralized datetime utilities untuk consistency."""

    @staticmethod
    def now_local() -> datetime:
        """Windows-safe current datetime untuk database operations."""
        return datetime.now()

    @staticmethod
    def parse_db_datetime(value: Any) -> datetime:
        """Parse datetime dari database - handle string/datetime conversion."""
        if isinstance(value, str):
            # Remove timezone suffix jika ada dari SQLite
            clean_value = value.replace("+07:00", "").replace("Z", "")
            try:
                return datetime.fromisoformat(clean_value)
            except ValueError as e:
                logger.warning(f"Failed to parse datetime: {value}, error: {e}")
                return datetime.now()

        if isinstance(value, datetime):
            return value

        # Fallback untuk unexpected types
        logger.warning(f"Unexpected datetime type: {type(value)}, value: {value}")
        return datetime.now()

    @staticmethod
    def expires_in_hours(hours: int = 8) -> datetime:
        """Calculate expiry datetime untuk session management."""
        return DateTimeUtils.now_local() + timedelta(hours=hours)

    @staticmethod
    def is_expired(expires_at: datetime | str) -> bool:
        """Check if datetime sudah expired."""
        if isinstance(expires_at, str):
            expires_at = DateTimeUtils.parse_db_datetime(expires_at)

        return DateTimeUtils.now_local() > expires_at


class DatabaseHelper:
    """Helper utilities untuk database operations."""

    @staticmethod
    def safe_commit(session) -> bool:
        """Safe commit dengan error handling."""
        try:
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            session.rollback()
            return False

    @staticmethod
    def ensure_single_result(result_list: list) -> Any | None:
        """Ensure query result contains single item."""
        if not result_list:
            return None

        if len(result_list) > 1:
            logger.warning(f"Expected single result, got {len(result_list)} items")

        return result_list[0]


# REMINDER: Shared constants untuk kedua domain
class DatabaseConstants:
    """Shared constants untuk database operations."""

    # Session durations
    DEFAULT_SESSION_HOURS = 8
    ADMIN_SESSION_HOURS = 12

    # Cache TTL
    CACHE_TTL_SHORT = 300  # 5 minutes
    CACHE_TTL_MEDIUM = 1800  # 30 minutes
    CACHE_TTL_LONG = 3600  # 1 hour


# PINNED: Export utilities untuk easy import
__all__ = [
    "DatabaseConstants",
    "DatabaseHelper",
    "DateTimeUtils",
]
