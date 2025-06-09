"""Logging setup untuk MIM3 Dashboard dengan konfigurasi via environment."""

from __future__ import annotations

import logging
import os
import sys

import streamlit as st
from loguru import logger

from config.paths import AppPaths


class InterceptHandler(logging.Handler):
    """Intercept standard logging ke Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Intercept standard logging messages and redirect them to Loguru.

        This method is called for each log message. It extracts the log level
        and message from the standard logging record and passes them to Loguru.

        Args:
            record (logging.LogRecord): The standard logging record.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


@st.cache_resource(show_spinner="Mengatur logging...")
def setup_logging() -> None:
    """Setup logging dengan centralized paths."""
    logger.remove()

    # Get config from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    separate_errors = os.getenv("LOG_SEPARATE_ERROR", "true").lower() == "true"

    # Hardcoded format (user tidak perlu tau)
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan> - <level>{message}</level>"
    )

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | {message}"
    )

    # 1. Console output (selalu ada, simplified untuk user)
    logger.add(
        sys.stderr,
        level=log_level,
        format=console_format,
        colorize=True,
        filter=lambda record: record["level"].name != "ERROR"
        if separate_errors
        else True,
    )

    if log_to_file:
        # ✅ Use centralized paths
        AppPaths.ensure_directories()

        # 2. General info logs (untuk dibaca di Streamlit)
        def is_info_success_warning_level(record):
            return record["level"].name in {"INFO", "SUCCESS", "WARNING"}

        logger.add(
            AppPaths.INFO_LOG,  # ✅ Centralized
            level="INFO",
            format=file_format,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            filter=is_info_success_warning_level,
            serialize=True,
        )

        if separate_errors:
            # 3. Error logs terpisah (untuk support)
            logger.add(
                AppPaths.ERROR_LOG,  # ✅ Centralized
                level="ERROR",
                format=file_format,
                rotation="50 MB",
                retention="90 days",  # Error logs disimpan lebih lama
                compression="zip",
                enqueue=True,
                backtrace=True,
                diagnose=True,  # Full debugging info untuk support
                serialize=False,  # Text format - mudah dibaca manual
            )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.success(
        f"Logging setup complete - Level: {log_level}, File: {log_to_file}, Separate errors: {separate_errors}"
    )
