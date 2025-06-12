"""User commands untuk database operations - standardized Pydantic returns."""

from __future__ import annotations

from datetime import datetime

import bcrypt
import streamlit as st
from loguru import logger
from sqlalchemy import delete, select, update

from config.constants import DBConstants
from database.definitions import get_role_table_definition, get_user_table_definition
from models.user.user_commons import OperationResult
from models.user.user_models import User, UserCreate, UserListItem, UserUpdate


@st.cache_data(ttl=DBConstants.CACHE_TTL_MEDIUM, show_spinner="Loading users...")
def get_all_users() -> list[UserListItem]:
    """Get semua users untuk admin listing."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        user_table = get_user_table_definition()
        role_table = get_role_table_definition()

        stmt = (
            select(
                user_table.c.id,
                user_table.c.username,
                user_table.c.name,
                role_table.c.name.label("role_name"),
                user_table.c.is_verified,
                user_table.c.is_active,
            )
            .select_from(
                user_table.join(role_table, user_table.c.role_id == role_table.c.id)
            )
            .order_by(user_table.c.created_at.desc())
        )

        with conn.session as s:
            results = s.execute(stmt).fetchall()

        return [UserListItem.model_validate(row._asdict()) for row in results]

    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return []


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Fetching user...")
def get_user_by_id(user_id: int) -> User | None:
    """Get user by ID dengan role name."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        user_table = get_user_table_definition()
        role_table = get_role_table_definition()

        stmt = (
            select(
                user_table.c.id,
                user_table.c.username,
                user_table.c.name,
                user_table.c.password_hash,
                user_table.c.role_id,
                role_table.c.name.label("role_name"),
                user_table.c.is_verified,
                user_table.c.is_active,
                user_table.c.created_at,
                user_table.c.updated_at,
            )
            .select_from(
                user_table.join(role_table, user_table.c.role_id == role_table.c.id)
            )
            .where(user_table.c.id == user_id)
        )

        with conn.session as s:
            result = s.execute(stmt).first()

        if result:
            return User.model_validate(result._asdict())
        return None

    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None


def create_user(user_data: UserCreate) -> OperationResult:
    """Create new user - admin operation dengan enhanced error logging."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        # Hash password
        logger.debug(f"Hashing password for user: {user_data.username}")
        password_hash = bcrypt.hashpw(
            user_data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        logger.debug("Password hashed successfully")

        with conn.session as s:
            # Check existing user
            logger.debug(f"Checking if username exists: {user_data.username}")
            check_stmt = select(user_table.c.id).where(
                user_table.c.username == user_data.username
            )
            existing = s.execute(check_stmt).fetchone()

            if existing:
                logger.debug(f"Username already exists: {user_data.username}")
                return OperationResult(
                    success=False, message=f"Username '{user_data.username}' sudah ada"
                )

            # Insert new user
            logger.debug(f"Inserting new user: {user_data.username}")
            insert_stmt = user_table.insert().values(
                username=user_data.username,
                name=user_data.name,
                password_hash=password_hash,
                role_id=user_data.role_id,
                is_verified=user_data.is_verified,
                is_active=user_data.is_active,  # ✅ Add this back - column exists!
                created_at=user_data.created_at,
                updated_at=user_data.created_at,
            )

            result = s.execute(insert_stmt)
            logger.debug(f"Insert executed, rows affected: {result.rowcount}")

            s.commit()
            logger.debug("Transaction committed successfully")

            logger.info(f"User created: {user_data.username}")
            return OperationResult(
                success=True, message=f"User '{user_data.username}' berhasil dibuat"
            )

    except Exception as e:
        logger.error(f"Failed to create user {user_data.username}: {e}")
        return OperationResult(success=False, message=f"Error creating user: {e!s}")


def update_user(user_id: int, user_data: UserUpdate) -> OperationResult:
    """Update user data - admin operation."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        # Build update values - hanya field yang tidak None
        update_values = {}
        if user_data.name is not None:
            update_values["name"] = user_data.name
        if user_data.role_id is not None:
            update_values["role_id"] = user_data.role_id
        if user_data.is_active is not None:
            update_values["is_active"] = user_data.is_active

        if not update_values:
            return OperationResult(
                success=False, message="Tidak ada data untuk diupdate"
            )

        update_values["updated_at"] = datetime.now()

        with conn.session as s:
            # Check user exists
            check_stmt = select(user_table.c.id).where(user_table.c.id == user_id)
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            # Update user
            update_stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(**update_values)
            )
            s.execute(update_stmt)
            s.commit()

            logger.info(f"User updated: {user_id}")
            return OperationResult(success=True, message="User berhasil diupdate")

    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        return OperationResult(success=False, message="Gagal mengupdate user")


def delete_user(user_id: int) -> OperationResult:
    """Delete user - admin operation."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            # Check user exists
            check_stmt = select(user_table.c.username).where(user_table.c.id == user_id)
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            username = existing[0]

            # Delete user
            delete_stmt = delete(user_table).where(user_table.c.id == user_id)
            s.execute(delete_stmt)
            s.commit()

            logger.info(f"User deleted: {username}")
            return OperationResult(
                success=True, message=f"User '{username}' berhasil dihapus"
            )

    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        return OperationResult(success=False, message="Gagal menghapus user")


def deactivate_user(user_id: int) -> OperationResult:
    """Deactivate user instead of delete - safer operation."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            # Check user exists and get username
            check_stmt = select(user_table.c.username, user_table.c.is_active).where(
                user_table.c.id == user_id
            )
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            username, is_active = existing

            if not is_active:
                return OperationResult(
                    success=False, message=f"User '{username}' sudah tidak aktif"
                )

            # Deactivate user
            update_stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(is_active=False, updated_at=datetime.now())
            )
            s.execute(update_stmt)
            s.commit()

            logger.info(f"User deactivated: {username}")
            return OperationResult(
                success=True, message=f"User '{username}' berhasil dinonaktifkan"
            )

    except Exception as e:
        logger.error(f"Failed to deactivate user {user_id}: {e}")
        return OperationResult(success=False, message="Gagal menonaktifkan user")


def activate_user(user_id: int) -> OperationResult:
    """Activate user - opposite of deactivate."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            # Check user exists
            check_stmt = select(user_table.c.username, user_table.c.is_active).where(
                user_table.c.id == user_id
            )
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            username, is_active = existing

            if is_active:
                return OperationResult(
                    success=False, message=f"User '{username}' sudah aktif"
                )

            # Activate user
            update_stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(is_active=True, updated_at=datetime.now())
            )
            s.execute(update_stmt)
            s.commit()

            logger.info(f"User activated: {username}")
            return OperationResult(
                success=True, message=f"User '{username}' berhasil diaktifkan"
            )

    except Exception as e:
        logger.error(f"Failed to activate user {user_id}: {e}")
        return OperationResult(success=False, message="Gagal mengaktifkan user")


def verify_user(user_id: int) -> OperationResult:
    """Verify user account."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            # Check user exists
            check_stmt = select(user_table.c.username, user_table.c.is_verified).where(
                user_table.c.id == user_id
            )
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            username, is_verified = existing

            if is_verified:
                return OperationResult(
                    success=False, message=f"User '{username}' sudah terverifikasi"
                )

            # Verify user
            update_stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(is_verified=True, updated_at=datetime.now())
            )
            s.execute(update_stmt)
            s.commit()

            logger.info(f"User verified: {username}")
            return OperationResult(
                success=True, message=f"User '{username}' berhasil diverifikasi"
            )

    except Exception as e:
        logger.error(f"Failed to verify user {user_id}: {e}")
        return OperationResult(success=False, message="Gagal memverifikasi user")


def unverify_user(user_id: int) -> OperationResult:
    """Unverify user account."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            # Check user exists
            check_stmt = select(user_table.c.username, user_table.c.is_verified).where(
                user_table.c.id == user_id
            )
            existing = s.execute(check_stmt).fetchone()

            if not existing:
                return OperationResult(success=False, message="User tidak ditemukan")

            username, is_verified = existing

            if not is_verified:
                return OperationResult(
                    success=False, message=f"User '{username}' belum terverifikasi"
                )

            # Unverify user
            update_stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(is_verified=False, updated_at=datetime.now())
            )
            s.execute(update_stmt)
            s.commit()

            logger.info(f"User unverfied: {username}")
            return OperationResult(
                success=True,
                message=f"User '{username}' berhasil dinonaktifkan verifikasinya",
            )

    except Exception as e:
        logger.error(f"Failed to unverify user {user_id}: {e}")
        return OperationResult(
            success=False, message="Gagal menonaktifkan verifikasi user"
        )


def has_any_admin_user() -> bool:
    """Check if there is any admin user in the system."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        user_table = get_user_table_definition()

        with conn.session as s:
            stmt = select(user_table.c.id).where(
                (user_table.c.role_id == 1) & (user_table.c.is_active)
            )
            result = s.execute(stmt).fetchone()

        return result is not None

    except Exception as e:
        logger.error(f"Failed to check admin users: {e}")
        return False
