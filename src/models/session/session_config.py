"""Session configuration dengan environment-aware defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SessionConfig:
    """Centralized session configuration dengan fallbacks."""

    # Session timing
    default_session_hours: int = 8
    idle_timeout_hours: int = 2
    cleanup_interval_hours: int = 24

    # Network defaults (LAN-focused)
    default_client_ip: str = "192.168.1.100"
    default_access_url: str = "http://192.168.1.100:8501"
    allowed_ip_ranges: tuple[str, ...] = (
        "127.0.0.1",  # Localhost
        "192.168.1.",  # Primary LAN range
        "192.168.0.",  # Secondary LAN range
        "10.",  # Private network
    )

    # Browser defaults
    default_user_agent: str = "MIM3Dashboard/1.0 (Windows NT 10.0; Win64; x64)"
    default_timezone: str = "Asia/Jakarta"
    default_timezone_offset: int = -420  # UTC+7
    default_locale: str = "id-ID"

    # Context extraction settings
    context_timeout_seconds: float = 2.0
    enable_context_fallback: bool = True
    log_context_failures: bool = True

    # Health check settings
    health_check_enabled: bool = True
    health_check_interval_minutes: int = 30


# ✅ Environment-aware configuration
def get_session_config() -> SessionConfig:
    """Get session configuration berdasarkan environment."""
    # Check if running in development
    is_development = (
        os.getenv("STREAMLIT_ENV") == "development"
        or os.getenv("DEBUG") == "true"
        or Path(".streamlit/config.toml").exists()
    )

    if is_development:
        return SessionConfig(
            default_client_ip="127.0.0.1",
            default_access_url="http://localhost:8501",
            default_user_agent="MIM3Dashboard/1.0 Development",
            health_check_interval_minutes=5,  # More frequent in dev
        )

    # Production LAN configuration
    return SessionConfig()


# ✅ Global instance
SESSION_CONFIG = get_session_config()


# ✅ Utility functions
def get_fallback_context() -> dict[str, Any]:
    """Get fallback context values."""
    config = SESSION_CONFIG

    return {
        "client_ip": config.default_client_ip,
        "user_agent": config.default_user_agent,
        "access_url": config.default_access_url,
        "timezone": config.default_timezone,
        "timezone_offset": config.default_timezone_offset,
        "locale": config.default_locale,
        "is_embedded": False,
    }


def is_allowed_ip(ip_address: str | None) -> bool:
    """Check if IP address is in allowed ranges."""
    if not ip_address:
        return True  # Localhost/None is always allowed

    config = SESSION_CONFIG
    return any(ip_address.startswith(range_) for range_ in config.allowed_ip_ranges)


def get_session_timeout_hours() -> int:
    """Get session timeout untuk current environment."""
    return SESSION_CONFIG.default_session_hours


# REMINDER: Centralized configuration untuk easy maintenance
# TODO: Add .env support untuk custom configuration
# PINNED: Default values optimized untuk Windows LAN deployment
