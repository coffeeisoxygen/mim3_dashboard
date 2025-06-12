"""Session operations menggunakan ORM models untuk auto datetime conversion."""

# from __future__ import annotations

# import streamlit as st
# from loguru import logger
# from sqlalchemy import select, update
# from sqlalchemy.orm import selectinload

# from config.constants import DBConstants
# from database.commons import DatabaseHelper, DateTimeUtils
# from database.orm.orm_users import UserAccountORM, UserSessionORM
# from models.session.session_db import SessionCreate, SessionResult, SessionValidation


# def create_session_orm(session_data: SessionCreate) -> SessionResult:
#     """Create database session menggunakan ORM dengan auto datetime conversion."""
#     try:
#         logger.debug(f"Creating session (ORM) for user_id: {session_data.user_id}")
#         logger.debug(f"Token: {session_data.session_token[:10]}...")

#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ Create session using ORM model
#             session_obj = UserSessionORM(
#                 user_id=session_data.user_id,
#                 session_token=session_data.session_token,
#                 ip_address=session_data.ip_address,
#                 user_agent=session_data.user_agent,
#                 created_at=DateTimeUtils.now_local(),
#                 expires_at=session_data.expires_at,  # Already datetime from SessionCreate
#                 last_activity=DateTimeUtils.now_local(),
#                 is_active=True,
#             )

#             s.add(session_obj)

#             if DatabaseHelper.safe_commit(s):
#                 logger.info(f"Session created (ORM): ID {session_obj.id}")
#                 return SessionResult.success_result(
#                     session_id=session_obj.id,
#                     token=session_obj.session_token,
#                     message="Database session berhasil dibuat",
#                 )
#             else:
#                 return SessionResult.error_result("Gagal commit session ke database")

#     except Exception as e:
#         logger.error(f"Failed to create session (ORM): {e}")
#         return SessionResult.error_result(f"Gagal membuat database session: {e!s}")


# def create_session_factory(
#     user_id: int, hours: int = 8, request_info: dict | None = None
# ) -> SessionResult:
#     """Create session menggunakan ORM factory method."""
#     try:
#         logger.debug(f"Creating session via factory for user_id: {user_id}")

#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ Use ORM factory method dengan proper datetime handling
#             session_obj = UserSessionORM.create_new_session(
#                 user_id=user_id, hours=hours, request_info=request_info
#             )

#             s.add(session_obj)

#             if DatabaseHelper.safe_commit(s):
#                 logger.info(f"Session created via factory: ID {session_obj.id}")
#                 return SessionResult.success_result(
#                     session_id=session_obj.id,
#                     token=session_obj.session_token,
#                     message="Session berhasil dibuat",
#                 )
#             else:
#                 return SessionResult.error_result("Gagal commit session")

#     except Exception as e:
#         logger.error(f"Failed to create session via factory: {e}")
#         return SessionResult.error_result(f"Error: {e!s}")


# def deactivate_session_orm(session_token: str) -> bool:
#     """Deactivate session menggunakan ORM model."""
#     try:
#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM query with update
#             stmt = (
#                 update(UserSessionORM)
#                 .where(UserSessionORM.session_token == session_token)
#                 .values(is_active=False, last_activity=DateTimeUtils.now_local())
#             )

#             result = s.execute(stmt)

#             if DatabaseHelper.safe_commit(s) and result.rowcount > 0:
#                 logger.info(f"Session deactivated (ORM): {session_token[:10]}...")
#                 return True
#             else:
#                 logger.warning(f"Session not found (ORM): {session_token[:10]}...")
#                 return False

#     except Exception as e:
#         logger.error(f"Failed to deactivate session (ORM): {e}")
#         return False


# @st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT)
# def get_session_by_token_orm(session_token: str) -> SessionValidation:
#     """Get session dengan user data menggunakan ORM - auto datetime conversion."""
#     try:
#         logger.debug(f"Querying session by token (ORM): {session_token[:10]}...")

#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM query dengan relationship loading
#             stmt = (
#                 select(UserSessionORM)
#                 .options(
#                     selectinload(UserSessionORM.user).selectinload(UserAccountORM.role)
#                 )
#                 .where(UserSessionORM.session_token == session_token)
#             )

#             session_obj = s.execute(stmt).scalar_one_or_none()

#             if not session_obj:
#                 logger.warning(f"No session found (ORM): {session_token[:10]}...")
#                 return SessionValidation.invalid_session("Session tidak ditemukan")

#             # ✅ Check using ORM business logic
#             if not session_obj.is_active:
#                 return SessionValidation.invalid_session("Session tidak aktif")

#             if session_obj.is_expired():  # ✅ Use ORM method - auto datetime handling
#                 return SessionValidation.expired_session()

#             # ✅ Valid session dengan relationship navigation
#             return SessionValidation.valid_session(
#                 user_id=session_obj.user_id,
#                 username=session_obj.user.username,
#                 role_name=session_obj.user.role.name,
#             )

#     except Exception as e:
#         logger.error(f"Error getting session by token (ORM): {e}")
#         return SessionValidation.invalid_session("Database error")


# def update_session_activity_orm(session_token: str) -> bool:
#     """Update last activity menggunakan ORM model."""
#     try:
#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM query untuk update activity
#             stmt = (
#                 update(UserSessionORM)
#                 .where(
#                     (UserSessionORM.session_token == session_token)
#                     & (UserSessionORM.is_active == True)
#                 )
#                 .values(last_activity=DateTimeUtils.now_local())
#             )

#             result = s.execute(stmt)
#             success = DatabaseHelper.safe_commit(s) and result.rowcount > 0

#             if success:
#                 logger.debug(f"Session activity updated (ORM): {session_token[:10]}...")
#             else:
#                 logger.warning(
#                     f"Failed to update activity (ORM): {session_token[:10]}..."
#                 )

#             return success

#     except Exception as e:
#         logger.error(f"Failed to update session activity (ORM): {e}")
#         return False


# @st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT)
# def is_session_expired_orm(session_token: str) -> bool:
#     """Quick check if session is expired menggunakan ORM."""
#     try:
#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM query untuk check expiry
#             stmt = select(UserSessionORM.expires_at).where(
#                 UserSessionORM.session_token == session_token
#             )

#             result = s.execute(stmt).scalar_one_or_none()

#             if not result:
#                 return True  # Session tidak ada = expired

#             # ✅ Use DateTimeUtils untuk consistent comparison
#             return DateTimeUtils.is_expired(result)

#     except Exception as e:
#         logger.error(f"Failed to check session expiry (ORM): {e}")
#         return True  # Failsafe - consider expired on error


# def get_active_sessions_orm(user_id: int | None = None) -> list[UserSessionORM]:
#     """Get active sessions untuk admin monitoring."""
#     try:
#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM query dengan optional user filter
#             stmt = (
#                 select(UserSessionORM)
#                 .options(selectinload(UserSessionORM.user))
#                 .where(UserSessionORM.is_active == True)
#             )

#             if user_id:
#                 stmt = stmt.where(UserSessionORM.user_id == user_id)

#             sessions = s.execute(stmt).scalars().all()

#             # ✅ Filter non-expired sessions using ORM method
#             active_sessions = [
#                 session for session in sessions if not session.is_expired()
#             ]

#             logger.debug(f"Found {len(active_sessions)} active sessions")
#             return active_sessions

#     except Exception as e:
#         logger.error(f"Failed to get active sessions (ORM): {e}")
#         return []


# def force_deactivate_user_sessions_orm(user_id: int) -> bool:
#     """Force deactivate all user sessions untuk admin control."""
#     try:
#         conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

#         with conn.session as s:
#             # ✅ ORM bulk update
#             stmt = (
#                 update(UserSessionORM)
#                 .where(UserSessionORM.user_id == user_id)
#                 .values(is_active=False, last_activity=DateTimeUtils.now_local())
#             )

#             result = s.execute(stmt)
#             success = DatabaseHelper.safe_commit(s)

#             if success:
#                 logger.info(
#                     f"Deactivated {result.rowcount} sessions for user {user_id}"
#                 )
#                 return True
#             else:
#                 logger.warning(f"Failed to deactivate sessions for user {user_id}")
#                 return False

#     except Exception as e:
#         logger.error(f"Failed to force deactivate user sessions (ORM): {e}")
#         return False


# # REMINDER: Legacy functions tetap ada untuk backward compatibility
# # TODO: Update session_service.py untuk use ORM functions
# # PINNED: Phase 2 - Remove legacy functions setelah semua service migrated
