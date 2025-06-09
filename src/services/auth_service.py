"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

from typing import TypedDict

import bcrypt
from loguru import logger

from models.auth import AuthResult, UserLogin, UserRole, UserSession


class DemoUserData(TypedDict):
    """Type hint untuk demo user data."""

    password_hash: bytes
    role: UserRole
    user_id: int


class AuthService:
    """Service untuk menangani authentication logic."""

    def __init__(self):
        """Initialize auth service dengan demo users."""
        # TODO: Nanti diganti dengan database
        self._demo_users: dict[str, DemoUserData] = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "role": "admin",
                "user_id": 1,
            },
            "user": {
                "password_hash": self._hash_password("user123"),
                "role": "user",
                "user_id": 2,
            },
            "manager": {
                "password_hash": self._hash_password("manager123"),
                "role": "manager",
                "user_id": 3,
            },
        }

    def authenticate(self, login_data: UserLogin) -> AuthResult:
        """Authenticate user dengan username dan password.

        Args:
            login_data: Data login dari user

        Returns:
            AuthResult dengan status authentication dan session data
        """
        try:
            # Check if user exists
            if login_data.username not in self._demo_users:
                logger.warning(
                    f"Login attempt with unknown username: {login_data.username}"
                )
                return AuthResult(
                    success=False, error_message="Username atau password salah"
                )

            user_data = self._demo_users[login_data.username]

            # Verify password
            if not self._verify_password(
                login_data.password, user_data["password_hash"]
            ):
                logger.warning(f"Failed login attempt for user: {login_data.username}")
                return AuthResult(
                    success=False, error_message="Username atau password salah"
                )

            # Create session
            session = UserSession(
                user_id=user_data["user_id"],
                username=login_data.username,
                role=user_data["role"],
            )

            logger.info(
                f"Successful login for user: {login_data.username} (role: {user_data['role']})"
            )

            return AuthResult(success=True, user_session=session)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(success=False, error_message="Terjadi kesalahan sistem")

    def _hash_password(self, password: str) -> bytes:
        """Hash password menggunakan bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def _verify_password(self, password: str, hashed: bytes) -> bool:
        """Verify password dengan hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
