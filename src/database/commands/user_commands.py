"""User commands untuk user operations."""

from __future__ import annotations

import streamlit as st
from loguru import logger
from sqlalchemy import insert, select, update

from config.constants import DBConstants
from database.definitions import get_role_table_definition, get_user_table_definition
from models.user import UserCreate, UserUpdate


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Fetching user...")
def get_user_by_id(user_id: int) -> dict | None:
    """Get user data by ID dengan role name."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    user_table = get_user_table_definition()
    role_table = get_role_table_definition()

    stmt = (
        select(
            user_table.c.id,
            user_table.c.username,
            user_table.c.name,
            user_table.c.is_verified,
            user_table.c.created_at,
            role_table.c.name.label("role_name"),  # ✅ JOIN untuk role_name
        )
        .select_from(
            user_table.join(role_table, user_table.c.role_id == role_table.c.id)
        )
        .where(user_table.c.id == user_id)
    )

    result = conn.query(str(stmt), params={"user_id": user_id})

    if result.empty:
        return None
    return result.to_dict(orient="records")[0]


def get_all_users() -> list[dict]:
    """Get all verified users."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    # ✅ SQLAlchemy table construct - safer from injection
    user_table = get_user_table_definition()

    stmt = (
        select(
            user_table.c.id,
            user_table.c.username,
            user_table.c.name,
            user_table.c.role_id,
        )
        .where(user_table.c.is_verified == 1)
        .order_by(user_table.c.id.asc())
    )

    result = conn.query(str(stmt))

    if result.empty:
        return []
    return result.to_dict(orient="records")


def create_user(user_data: UserCreate) -> tuple[bool, str]:
    """Create new user - returns (success, message)."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    try:
        with conn.session as s:
            # ✅ SQLAlchemy table construct - safer from injection
            user_table = get_user_table_definition()

            stmt = insert(user_table).values(
                username=user_data.username,
                name=user_data.name,
                password_hash=user_data.password,  # Will be hashed in service
                role_id=user_data.role_id,
                is_verified=False,
            )

            s.execute(stmt)
            s.commit()
            logger.info(f"User created: {user_data.username}")
            return True, "User berhasil dibuat"

    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return False, "Gagal membuat user"


def update_user(user_id: int, user_data: UserUpdate) -> tuple[bool, str]:
    """Update user data - returns (success, message)."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    try:
        with conn.session as s:
            # Build update values dict based on provided fields
            update_values = {}

            if user_data.name is not None:
                update_values["name"] = user_data.name

            if user_data.role_id is not None:
                update_values["role_id"] = user_data.role_id

            if user_data.is_verified is not None:
                update_values["is_verified"] = user_data.is_verified

            if not update_values:
                return False, "Tidak ada data yang diupdate"

            user_table = get_user_table_definition()

            stmt = (
                update(user_table)
                .where(user_table.c.id == user_id)
                .values(update_values)
            )
            s.execute(stmt)
            s.commit()

            logger.info(f"User updated: {user_id}")
            return True, "User berhasil diupdate"

    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        return False, "Gagal mengupdate user"


def delete_user(user_id: int) -> bool:
    """Delete user by ID - returns success status."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    try:
        with conn.session as s:
            # ✅ SQLAlchemy table construct - safer from injection
            user_table = get_user_table_definition()

            stmt = user_table.delete().where(user_table.c.id == user_id)
            s.execute(stmt)
            s.commit()
            return True
    except Exception:
        return False
