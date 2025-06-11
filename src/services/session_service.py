"""Session service untuk hybrid session management - pure business logic."""

from __future__ import annotations

from loguru import logger

from database.commands.session_commands import (
    create_session,
    deactivate_session,
    get_session_by_token,
    is_session_expired,
    update_session_activity,
)
from models.session.session_db import SessionCreate, SessionResult, SessionValidation
from models.user.user_auth import ActiveSession


class SessionService:
    """Pure business logic untuk session management - no UI dependencies."""

    @logger.catch
    def create_user_session(
        self, user_session: ActiveSession, request_info: dict | None = None
    ) -> SessionResult:
        """Create database session dengan audit trail."""
        try:
            # Step 1: Prepare session data
            session_data = self._prepare_session_data(user_session, request_info)

            # Step 2: Create database session
            db_result = create_session(session_data)
            if not db_result.success:
                logger.warning(f"Database session creation failed: {db_result.message}")
                return db_result

            # Step 3: Validate result
            if db_result.session_id is None or db_result.token is None:
                logger.error("Database session created but missing data")
                return SessionResult.error_result(
                    "Error sistem: data session tidak valid"
                )

            logger.info(f"Database session created for user: {user_session.username}")
            return db_result

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return SessionResult.error_result("Error sistem saat membuat session")

    def validate_session(self, session_token: str | None) -> SessionValidation:
        """Validate session dengan database check."""
        if not session_token:
            return SessionValidation.invalid_session("Token tidak ada")

        return get_session_by_token(session_token)

    def refresh_session(self, session_token: str | None) -> bool:
        """Refresh session activity untuk keep alive."""
        if not session_token:
            return False

        if is_session_expired(session_token):
            logger.info(f"Session expired, cannot refresh: {session_token[:10]}...")
            return False

        success = update_session_activity(session_token)
        if success:
            logger.opt(lazy=True).debug(
                "Session refreshed: {token}", token=lambda: session_token[:10]
            )

        return success

    def deactivate_session(self, session_token: str | None) -> bool:
        """Deactivate database session."""
        if not session_token:
            return True  # Nothing to deactivate

        success = deactivate_session(session_token)
        if success:
            logger.info(f"Database session deactivated: {session_token[:10]}...")
        else:
            logger.warning(f"Failed to deactivate session: {session_token[:10]}...")

        return success

    def get_session_restoration_data(self, session_token: str) -> SessionValidation:
        """Get validation data untuk UI restoration - returns data only."""
        logger.debug(f"Getting restoration data: {session_token[:10]}...")

        validation = self.validate_session(session_token)

        if validation.is_valid:
            # Refresh activity saat restoration
            self.refresh_session(session_token)
            logger.info(f"Restoration data ready for: {validation.username}")

        return validation

    def _prepare_session_data(
        self, user_session: ActiveSession, request_info: dict | None
    ) -> SessionCreate:
        """Prepare session data dengan request info."""
        logger.debug(f"Preparing session data for user_id: {user_session.user_id}")

        session_data = SessionCreate.create_new(
            user_id=user_session.user_id,
            hours=8,  # 8 jam kerja
            request_info=request_info,
        )

        logger.opt(lazy=True).debug(
            "Session data prepared: token={token}, expires={expires}",
            token=lambda: session_data.session_token[:10],
            expires=lambda: session_data.expires_at,
        )

        return session_data


# REMINDER: Removed UI-dependent methods (restore_session_from_token, ensure_session_active, sync_session_state)
# TODO: Move UI orchestration methods ke SessionRestorationManager
