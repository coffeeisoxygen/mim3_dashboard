"""Simplified logging setup tanpa session tracking."""

import logging
import os
import sys
import warnings

import streamlit as st
from loguru import logger

from config.paths import AppPaths

from .filters import error_filter, info_filter, streamlit_filter
from .handlers import InterceptHandler, handle_exception


@st.cache_resource(show_spinner="Mengatur logging...")
def setup_logging() -> None:
    """Setup logging untuk MIM3 Dashboard - simplified version."""
    # Tangkap uncaught exceptions
    sys.excepthook = handle_exception

    # Tangkap warnings.warn()
    def show_warning(message, *args, **kwargs):  # noqa: ARG001
        logger.warning(str(message))

    warnings.showwarning = show_warning

    logger.remove()

    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    separate_errors = os.getenv("LOG_SEPARATE_ERROR", "true").lower() == "true"

    # ✅ Simplified console format - no session ID dependency
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<magenta>{function}</magenta>:<yellow>{line}</yellow> - "
        "<level>{message}</level>"
    )

    # ✅ Simplified file format - no session ID dependency
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | {message}"
    )

    # 1. Console logging
    logger.add(
        sys.stderr,
        level=log_level,
        format=console_format,
        colorize=True,
        filter=lambda r: streamlit_filter(r)
        and (error_filter(r) if separate_errors else True),
    )

    if log_to_file:
        AppPaths.ensure_directories()

        # 2. Info log file
        logger.add(
            AppPaths.INFO_LOG,
            level="INFO",
            format=file_format,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            serialize=True,
            filter=info_filter,
        )

        if separate_errors:
            # 3. Error log file
            logger.add(
                AppPaths.ERROR_LOG,
                level="ERROR",
                format=file_format,
                rotation="50 MB",
                retention="90 days",
                compression="zip",
                enqueue=True,
                serialize=False,
                backtrace=True,
                diagnose=True,
            )

    # Intercept standard logging → Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.success(
        f"✅ Logging setup complete - Level: {log_level}, File logging: {log_to_file}"
    )


# ✅ Helper function untuk request-specific context
def get_contextual_logger(
    *,
    user_id: int | None = None,
    username: str | None = None,
    operation: str | None = None,
    module: str | None = None,
):
    """Get logger dengan request-specific context."""
    context = {}

    if user_id:
        context["user_id"] = user_id
    if username:
        context["username"] = username
    if operation:
        context["operation"] = operation
    if module:
        context["module"] = module

    return logger.bind(**context) if context else logger


# ✅ Usage examples with better context
# service_logger = get_contextual_logger(module="authentication", operation="login")
# service_logger.info("Login attempt", username="admin")

# with logger.contextualize(user_id=123, operation="password_change"):
#     logger.info("Password change initiated")
#     logger.info("Password validation passed")
