"""Main logging setup untuk MIM3 Dashboard."""

import logging
import os
import sys
import threading
import warnings

import streamlit as st
from loguru import logger

from config.paths import AppPaths

from .filters import error_filter, info_filter, streamlit_filter
from .handlers import InterceptHandler, handle_exception

# Thread-local storage untuk session tracking
_local = threading.local()


def get_session_id() -> str:
    """Generate atau retrieve session ID untuk tracking."""
    try:
        # Prioritas: streamlit session state
        if hasattr(st, "session_state") and st.session_state:
            if "session_id" not in st.session_state:
                import uuid

                st.session_state.session_id = str(uuid.uuid4())[:8]
            return st.session_state.session_id
    except Exception:  # noqa: S110
        pass

    # Fallback: thread-local storage
    if not hasattr(_local, "session_id"):
        import uuid

        _local.session_id = str(uuid.uuid4())[:8]

    return _local.session_id


@st.cache_resource(show_spinner="Mengatur logging...")
def setup_logging() -> None:
    """Setup logging untuk MIM3 Dashboard dengan Loguru + Streamlit."""
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

    # Console format
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<blue>[{extra[session_id]}]</blue> | "
        "<cyan>{name}</cyan>:<magenta>{function}</magenta>:<yellow>{line}</yellow> - "
        "<level>{message}</level>"
    )

    # File format
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "[{extra[session_id]}] | "
        "{name}:{function}:{line} | {message}"
    )

    # 1. Console: dengan filter
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

        # 2. Log file umum (INFO, SUCCESS, WARNING)
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
            # 3. Log error terpisah (ERROR+)
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

    # Configure dengan session context
    session_id = get_session_id()
    logger.configure(extra={"session_id": session_id})

    logger.success(
        f"✅ Logging setup complete - Level: {log_level}, File logging: {log_to_file}"
    )
