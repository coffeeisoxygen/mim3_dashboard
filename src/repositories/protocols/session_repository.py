"""Session repository protocol untuk abstraction layer."""

from __future__ import annotations

from typing import Protocol

from models.session.session_db import SessionCreate, SessionResult, SessionValidation


class SessionRepository(Protocol):
    """Protocol untuk session data access operations.

    Defines interface untuk session management yang bisa di-implement
    dengan berbagai teknologi (ORM, raw SQL, etc.) tanpa break service layer.
    """

    def get_session_by_token(self, session_token: str) -> SessionValidation:
        """Get session dengan user data untuk validation.

        Args:
            session_token: Token untuk identify session

        Returns:
            SessionValidation dengan user data dan validity status
        """
        ...

    def create_session(self, session_data: SessionCreate) -> SessionResult:
        """Create new database session.

        Args:
            session_data: Session creation data dengan user_id dan expiry

        Returns:
            SessionResult dengan success status dan session token
        """
        ...

    def deactivate_session(self, session_token: str) -> bool:
        """Deactivate existing session.

        Args:
            session_token: Token untuk identify session yang akan di-deactivate

        Returns:
            True jika berhasil deactivate, False jika session not found
        """
        ...

    def update_session_activity(self, session_token: str) -> bool:
        """Update last activity timestamp untuk session.

        Args:
            session_token: Token untuk identify session

        Returns:
            True jika berhasil update activity
        """
        ...

    def is_session_expired(self, session_token: str) -> bool:
        """Quick check jika session sudah expired.

        Args:
            session_token: Token untuk check expiry

        Returns:
            True jika expired atau not found
        """
        ...

    def get_active_sessions(self, user_id: int | None = None) -> list[dict]:
        """Get active sessions untuk monitoring.

        Args:
            user_id: Optional filter untuk specific user

        Returns:
            List session data untuk admin monitoring
        """
        ...

    def force_deactivate_user_sessions(self, user_id: int) -> bool:
        """Force deactivate semua user sessions.

        Args:
            user_id: User yang sessions-nya akan di-deactivate

        Returns:
            True jika berhasil deactivate sessions
        """
        ...


# REMINDER: Protocol ini define contract, bukan implementation
# TODO: Create SessionRepositoryORM implementation
# TODO: Create SessionRepositoryLegacy implementation untuk fallback
# PINNED: Update SessionService untuk use protocol dependency injection
