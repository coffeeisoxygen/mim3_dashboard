"""Centralized path configuration untuk MIM3 Dashboard."""

from __future__ import annotations

from pathlib import Path


class AppPaths:
    """Centralized path management untuk Windows compatibility."""

    # ✅ Base application directory
    APP_ROOT = Path.cwd()

    # ✅ Data directories
    DATA_DIR = APP_ROOT / "data"
    TEMP_DIR = APP_ROOT / "temp"
    LOGS_DIR = APP_ROOT / "logs"

    # ✅ Session management
    SESSIONS_DIR = TEMP_DIR / "sessions"

    # ✅ Database paths
    DATABASE_FILE = DATA_DIR / "mim3.db"
    DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

    # ✅ Log files
    INFO_LOG = LOGS_DIR / "mim3_info.log"
    ERROR_LOG = LOGS_DIR / "mim3_errors.log"

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required directories."""
        for path in [cls.DATA_DIR, cls.TEMP_DIR, cls.LOGS_DIR, cls.SESSIONS_DIR]:
            path.mkdir(parents=True, exist_ok=True)
