"""Konstanta global untuk seluruh aplikasi."""

from __future__ import annotations


class DBConstants:
    """Global constants untuk MIM3 Dashboard."""

    # Database connection constants
    CON_NAME = "mim3_db"
    CON_TYPE = "sql"
    CON_TTL = 300  # TTL dalam detik, sebagai integer

    # Cache TTL constants
    CACHE_TTL_SHORT = 300  # 5 menit
    CACHE_TTL_MEDIUM = 1800  # 30 menit
    CACHE_TTL_LONG = 3600  # 1 jam
    CACHE_TTL_FAST = 60  # 1 menit untuk session validation


class LogConstants:
    """Log file constants untuk MIM3 Dashboard."""

    # Log file names
    INFO_LOG_FILE = "mim3_info.log"
    ERROR_LOG_FILE = "mim3_errors.log"

    # Log file paths
    INFO_LOG_PATH = f"logs/{INFO_LOG_FILE}"
    ERROR_LOG_PATH = f"logs/{ERROR_LOG_FILE}"

    # Log levels
    LOG_LEVEL_INFO = "INFO"
    LOG_LEVEL_ERROR = "ERROR"
    LOG_LEVEL_DEBUG = "DEBUG"
