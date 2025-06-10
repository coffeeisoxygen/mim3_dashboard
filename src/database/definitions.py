"""Shared table definitions untuk eliminate redundancy."""

from sqlalchemy import column, table

USER_TABLE = table(
    "user_account",
    column("id"),
    column("username"),
    column("name"),
    column("password_hash"),
    column("role_id"),
    column("is_verified"),
    column("created_at"),
    column("updated_at"),
)

ROLE_TABLE = table(
    "role",
    column("id"),
    column("name"),
    column("description"),
    column("is_active"),
    column("created_at"),
)

USER_SESSION_TABLE = table(
    "user_session",
    column("id"),
    column("user_id"),
    column("session_token"),
    column("ip_address"),
    column("user_agent"),
    column("created_at"),
    column("expires_at"),
    column("last_activity"),
    column("is_active"),
)


# Helper functions
def get_user_table_definition():
    """Get user table definition."""
    return USER_TABLE


def get_role_table_definition():
    """Get role table definition."""
    return ROLE_TABLE


def get_session_table_definition():
    """Get session table definition."""
    return USER_SESSION_TABLE
