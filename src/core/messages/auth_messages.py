"""Centralized messages untuk MIM3 Dashboard."""

from __future__ import annotations


class AuthMessages:
    """Authentication related messages."""

    # Validation messages
    REQUIRED_FIELDS = "Username dan password harus diisi"
    INVALID_INPUT = "Format input tidak valid"

    # Authentication messages
    LOGIN_SUCCESS = "Login berhasil"
    LOGIN_FAILED = "Username atau password salah"
    LOGOUT_SUCCESS = "Logout berhasil"

    # System messages
    SYSTEM_ERROR = "Terjadi kesalahan sistem"
    SESSION_EXPIRED = "Sesi telah berakhir"


class UIMessages:
    """UI related messages."""

    # Actions
    CONFIRM_LOGOUT = "Yakin ingin logout dari MIM3 Dashboard?"
    LOADING = "Memuat data..."
    SAVING = "Menyimpan data..."

    # Status
    SUCCESS_PREFIX = "✅"
    ERROR_PREFIX = "❌"
    WARNING_PREFIX = "⚠️"
    INFO_PREFIX = "ℹ️"  # noqa: RUF001
