"""Session service dengan repository pattern - pure business logic."""

from __future__ import annotations

from loguru import logger

from models.session.session_context import SessionContext
from models.session.session_db import SessionCreate, SessionResult, SessionValidation
from models.user.user_auth import UserActiveSession
from repositories.protocols.session_repository import SessionRepository


class SessionService:
    """Pure business logic untuk session management dengan dependency injection."""

    def __init__(self, repository: SessionRepository):
        """Initialize service dengan repository dependency."""
        self.repo = repository

    def create_user_session(
        self, user_session: UserActiveSession, context: SessionContext | None = None
    ) -> SessionResult:
        """Create database session dengan rich context audit trail."""
        try:
            # Step 1: Use context or create from current request
            session_context = context or SessionContext.from_streamlit_context()

            # Step 2: Prepare session data dengan rich context
            session_data = self._prepare_session_with_context(
                user_session, session_context
            )

            # Step 3: Create database session via repository
            db_result = self.repo.create_session(session_data)
            if not db_result.success:
                logger.warning(f"Database session creation failed: {db_result.message}")
                return db_result  # ✅ Return repository result directly

            # Step 4: Log dengan rich context info
            logger.info(
                f"Database session created for user: {user_session.username}",
                client_info=session_context.get_client_info(),
                local_access=session_context.is_local_access(),
                timezone=session_context.get_display_timezone(),
            )

            return db_result

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return SessionResult.error_result("Error sistem saat membuat session")

    def _prepare_session_with_context(
        self, user_session: UserActiveSession, context: SessionContext
    ) -> SessionCreate:
        """Prepare session data dengan rich SessionContext."""
        logger.debug(f"Preparing session data for user_id: {user_session.user_id}")

        # Rich request info dari SessionContext - ensure string conversion and validation
        ip_str = str(context.client_ip) if context.client_ip else None
        user_agent_str = str(context.user_agent) if context.user_agent else None

        # Truncate if too long (for test compatibility)
        if ip_str and len(ip_str) > 45:
            ip_str = ip_str[:45]
        if user_agent_str and len(user_agent_str) > 500:
            user_agent_str = user_agent_str[:500]

        request_info = {
            "ip_address": ip_str,
            "user_agent": user_agent_str,
        }

        session_data = SessionCreate.create_new(
            user_id=user_session.user_id,
            hours=8,  # 8 jam kerja
            request_info=request_info,  # Rich context data
        )

        logger.opt(lazy=True).debug(
            "Session data prepared: token={token}, expires={expires}",
            token=lambda: session_data.session_token[:10],
            expires=lambda: session_data.expires_at,
        )

        return session_data

    def validate_session(self, session_token: str | None) -> SessionValidation:
        """Validate session token dan return user session data."""
        if not session_token:
            return SessionValidation.invalid_session("Token tidak ada")

        return self.repo.get_session_by_token(session_token)

    def refresh_session(self, session_token: str) -> bool:
        """Refresh session activity timestamp."""
        if self.repo.is_session_expired(session_token):
            return False

        return self.repo.update_session_activity(session_token)

    def force_logout_user(self, user_id: int) -> bool:
        """Force logout semua sessions untuk user."""
        return self.repo.force_deactivate_user_sessions(user_id)

    def get_active_sessions_for_monitoring(
        self, user_id: int | None = None
    ) -> list[dict]:
        """Get active sessions untuk admin monitoring."""
        return self.repo.get_active_sessions(user_id)
