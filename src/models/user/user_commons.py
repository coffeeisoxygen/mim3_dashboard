"""Common utilities untuk User domain - pure utilities only."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field

# ================================
# Generic Operation Results
# ================================


class OperationResult(BaseModel):
    """Standard operation result pattern - generic untuk semua domains."""

    success: bool = Field(description="Operation berhasil atau tidak")
    message: str | None = Field(default=None, description="Pesan hasil operation")


# ================================
# System Configuration (Non-Role Specific)
# ================================


@dataclass(frozen=True)
class SystemConfiguration:
    """System configuration dengan general business rules."""

    min_password_length: int = 6
    max_password_length: int = 20
    require_admin_reason_min_length: int = 10
    session_timeout_hours: int = 24
    max_login_attempts: int = 5


# ✅ Default instance
SYSTEM_CONFIG = SystemConfiguration()


# ================================
# Generic Utilities
# ================================


def get_system_config() -> SystemConfiguration:
    """Get system configuration."""
    return SYSTEM_CONFIG


# REMINDER: Keep commons pure - no domain-specific logic
# TODO: Add validation utilities jika dibutuhkan multiple domains
# PINNED: OperationResult tetap generic untuk reusability across domains
