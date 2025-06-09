"""Database commands untuk authentication operations."""

from __future__ import annotations

import streamlit as st
from sqlalchemy import text

from config.constants import DBConstants


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Fetching user...")
def get_user_by_username(username: str) -> dict | None:
    """Get user data untuk authentication."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    stmt = text("""
        SELECT u.id, u.username, u.name, u.password_hash, u.role_id
        FROM user_account u
        WHERE u.username = :username AND u.is_verified = 1
    """)

    result = conn.query(str(stmt), params={"username": username})

    # ✅ More readable untuk single record
    if result.empty:
        return None
    return result.to_dict(orient="records")[0]
