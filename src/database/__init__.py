"""Database package untuk MIM3 Dashboard."""

from .connection import get_connection, initialize_database

__all__ = ["get_connection", "initialize_database"]
