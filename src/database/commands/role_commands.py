"""Database commands untuk role operations."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
from loguru import logger
from sqlalchemy import insert, select

from config.constants import DBConstants
from database.definitions import get_role_table_definition
from models.role.role_schemas import RoleCreate, RoleView


@st.cache_data(ttl=DBConstants.CACHE_TTL_LONG, show_spinner="Loading roles...")
def get_all_roles() -> list[RoleView]:
    """Get all active roles."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    role_table = get_role_table_definition()

    stmt = select(
        role_table.c.id,
        role_table.c.name,
        role_table.c.description,
        role_table.c.is_active,
        role_table.c.created_at,
    ).where(role_table.c.is_active == 1)

    with conn.session as s:
        results = s.execute(stmt).fetchall()

    return [RoleView.model_validate(row) for row in results]


@st.cache_data(ttl=DBConstants.CACHE_TTL_LONG, show_spinner="Loading roles...")
def get_roles_excluding_names(excluded_names: list[str]) -> list[RoleView]:
    """Get roles excluding specified names (untuk registration)."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    role_table = get_role_table_definition()

    stmt = select(
        role_table.c.id,
        role_table.c.name,
        role_table.c.description,
        role_table.c.is_active,
        role_table.c.created_at,
    ).where((role_table.c.is_active == 1) & (~role_table.c.name.in_(excluded_names)))

    with conn.session as s:
        results = s.execute(stmt).fetchall()

    return [RoleView.model_validate(row) for row in results]


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Loading role...")
def get_role_by_id(role_id: int) -> RoleView | None:
    """Get role by ID."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    role_table = get_role_table_definition()

    stmt = select(
        role_table.c.id,
        role_table.c.name,
        role_table.c.description,
        role_table.c.is_active,
        role_table.c.created_at,
    ).where(role_table.c.id == role_id)

    with conn.session as s:
        result = s.execute(stmt).first()

    if result:
        return RoleView.model_validate(result)
    else:
        logger.warning(f"Role not found: {role_id}")
        return None


def create_role(role_data: RoleCreate) -> tuple[bool, str]:
    """Create new role."""
    conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
    role_table = get_role_table_definition()

    try:
        logger.debug(f"Attempting to create role: {role_data.name}")  # ✅ Add debug

        with conn.session as s:
            stmt = insert(role_table).values(
                name=role_data.name,
                description=role_data.description,
                is_active=True,
                created_at=datetime.now(),
            )

            # ✅ Debug the actual SQL
            logger.debug(f"SQL statement: {stmt}")
            logger.debug(f"Values: name={role_data.name}, desc={role_data.description}")

            result = s.execute(stmt)
            logger.debug(
                f"Insert result rowcount: {result.rowcount}"
            )  # ✅ Check execution

            s.commit()
            logger.debug(f"Transaction committed for role: {role_data.name}")

        logger.info(f"Role created successfully: {role_data.name}")
        return True, f"Role '{role_data.name}' created successfully"

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            logger.debug(f"Role '{role_data.name}' already exists - skipping")
            return (
                True,
                f"Role '{role_data.name}' already exists",
            )  # ✅ Success for seeding
        else:
            logger.error(f"Failed to create role {role_data.name}: {e}")
            return False, f"Failed to create role: {e!s}"
