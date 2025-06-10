"""Session service untuk hybrid session management."""

from __future__ import annotations

from loguru import logger

from database.commands.session_commands import create_session, deactivate_session
from models.session.session_db import SessionCreate, SessionResult
from models.session.session_st import clear_user_session, set_user_session
from models.user.user_auth import ActiveSession


class SessionService:
    """Service untuk hybrid session management - orchestrates DB + Streamlit."""

    def create_user_session(
        self, user_session: ActiveSession, request_info: dict | None = None
    ) -> SessionResult:
        """Create hybrid session dengan atomic operation."""
        try:
            # Step 1: Prepare database session data
            session_data = self._prepare_session_data(user_session, request_info)

            # Step 2: Create database session (audit trail)
            db_result = create_session(session_data)
            if not db_result.success:
                logger.warning(f"Database session creation failed: {db_result.message}")
                return db_result

            # Step 3: Update ActiveSession dengan token dari database
            user_session.session_token = db_result.token

            # Step 4: Set Streamlit session state
            set_user_session(user_session)

            logger.info(f"Hybrid session created for user: {user_session.username}")
            return SessionResult.success_result(
                session_id=db_result.session_id,
                token=db_result.token,
                message="Hybrid session berhasil dibuat",
            )

        except Exception as e:
            logger.error(f"Failed to create hybrid session: {e}")
            return SessionResult.error_result("Error sistem saat membuat session")

    def clear_user_session(self, session_token: str | None = None) -> bool:
        """Clear hybrid session dengan graceful handling."""
        logger.debug(f"Starting session clear - Token: {bool(session_token)}")

        try:
            # Step 1: Clear Streamlit session (always safe)
            clear_user_session()
            logger.debug("Streamlit session cleared")

            # Step 2: Deactivate database session (if token exists)
            if session_token:
                db_success = deactivate_session(session_token)
                if db_success:
                    logger.info(
                        f"Database session deactivated: {session_token[:10]}..."
                    )
                else:
                    logger.warning(
                        f"Failed to deactivate DB session: {session_token[:10]}..."
                    )

            logger.info("Hybrid session cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Session clear error: {e}")
            # Return True karena Streamlit session udah clear (partial success)
            return True

    def _prepare_session_data(
        self, user_session: ActiveSession, request_info: dict | None
    ) -> SessionCreate:
        """Prepare session data dengan request info."""
        session_data = SessionCreate.create_new(
            user_id=user_session.user_id,
            hours=8,  # 8 jam kerja
            request_info=request_info,
        )
        return session_data

    # PINNED: Phase 2 - Admin session monitoring
    # TODO: get_active_sessions() untuk admin monitoring
    # TODO: force_logout_user() untuk admin control
