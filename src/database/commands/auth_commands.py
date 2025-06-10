"""Database commands untuk authentication operations."""

from __future__ import annotations

import streamlit as st
from loguru import logger
from sqlalchemy import select

from config.constants import DBConstants
from database.definitions import get_role_table_definition, get_user_table_definition
from models.user.user_models import User


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Fetching user...")
def get_user_by_username(username: str) -> User | None:
    """Get user data untuk authentication."""
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
            user_table.c.created_at,
            user_table.c.updated_at,
        )
        .select_from(
            user_table.join(role_table, user_table.c.role_id == role_table.c.id)
        )
        .where((user_table.c.username == username) & (user_table.c.is_verified == 1))
    )

    with conn.session as s:
        result = s.execute(stmt).first()

    if result:
        return User.model_validate(result)
    else:
        logger.warning(f"User not found or not verified: {username}")
        return None
