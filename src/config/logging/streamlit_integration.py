"""Integration antara Loguru dan Streamlit UI."""

import streamlit as st
from loguru import logger


class StreamlitLogDelegate:
    """Delegate pattern untuk forward logs ke Streamlit UI."""

    def __init__(self, show_user_messages: bool = True):
        self.show_user_messages = show_user_messages

    def info(self, message: str, *, user_message: str | None = None, **kwargs):
        """Log ke Loguru + optional tampilkan di UI."""
        logger.info(message, **kwargs)
        if self.show_user_messages and user_message:
            st.info(f"ℹ️ {user_message}")  # noqa: RUF001

    def success(self, message: str, *, user_message: str | None = None, **kwargs):
        """Log success + tampilkan di UI."""
        logger.success(message, **kwargs)
        if self.show_user_messages and user_message:
            st.success(f"✅ {user_message}")

    def warning(self, message: str, *, user_message: str | None = None, **kwargs):
        """Log warning + tampilkan di UI."""
        logger.warning(message, **kwargs)
        if self.show_user_messages and user_message:
            st.warning(f"⚠️ {user_message}")

    def error(self, message: str, *, user_message: str | None = None, **kwargs):
        """Log error + tampilkan di UI."""
        logger.error(message, **kwargs)
        if self.show_user_messages and user_message:
            st.error(f"❌ {user_message}")


# Global instance
st_logger = StreamlitLogDelegate()

# Usage examples:
# st_logger.info("Database connected", user_message="Successfully connected to database")
# st_logger.error("Database connection failed", user_message="Unable to connect. Please try again.")
