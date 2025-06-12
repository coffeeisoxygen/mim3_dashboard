"""Test fixtures untuk session testing - updated untuk session layer."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from models.session.session_context import SessionContext
from models.session.session_db import SessionResult, SessionValidation
from models.user.user_auth import UserActiveSession
from repositories.protocols.session_repository import SessionRepository
from services.session_service import SessionService


@pytest.fixture
def mock_repository():
    """Mock repository untuk testing."""
    return Mock(spec=SessionRepository)


@pytest.fixture
def session_service(mock_repository):
    """SessionService instance dengan mocked repository."""
    return SessionService(mock_repository)


@pytest.fixture
def sample_user_session():
    """Sample UserActiveSession untuk testing - with all required fields."""
    return UserActiveSession(
        user_id=1,
        username="test_user",
        name="Test User",
        role_id=2,
        role_name="staff",
        login_time=datetime.now(),
        session_token="existing_token",
    )


@pytest.fixture
def sample_session_context():
    """Sample SessionContext untuk testing - realistic data."""
    return SessionContext(
        client_ip="192.168.1.100",
        user_agent="Mozilla/5.0 Test Browser",
        access_url="http://192.168.1.100:8501",
        timezone="Asia/Jakarta",
        timezone_offset=-420,
        locale="id-ID",
        headers={"user-agent": "Mozilla/5.0 Test Browser"},
        cookies={},
        is_embedded=False,
    )


@pytest.fixture
def sample_session_context_with_long_strings():
    """SessionContext dengan long strings untuk testing validation."""
    return SessionContext(
        client_ip="very.long.ip.address.that.exceeds.normal.length.limit.test",
        user_agent="very" * 200,  # Very long user agent
        access_url="http://very.long.domain.name.that.exceeds.normal.url.length/path",
        timezone="Asia/Jakarta",
        locale="id-ID",
        is_embedded=False,
    )


@pytest.fixture
def sample_session_context_with_none_values():
    """SessionContext dengan None values untuk testing fallbacks."""
    return SessionContext(
        client_ip=None,
        user_agent=None,
        access_url=None,
        timezone=None,
        locale=None,
        is_embedded=False,
    )


@pytest.fixture
def valid_session_result():
    """Valid SessionResult untuk mock responses."""
    return SessionResult(
        success=True,
        message="Session created successfully",
        session_id=1,
        token="new_session_token",
    )


@pytest.fixture
def valid_session_validation():
    """Valid SessionValidation untuk mock responses."""
    return SessionValidation(
        is_valid=True,
        is_expired=False,
        user_id=1,
        username="test_user",
        role_name="staff",
        message="Session valid",
    )


@pytest.fixture
def error_session_result():
    """Error SessionResult untuk testing failures."""
    return SessionResult(
        success=False,
        message="Database connection failed",
        session_id=None,
        token=None,
    )


@pytest.fixture
def invalid_session_validation():
    """Invalid SessionValidation untuk testing."""
    return SessionValidation(
        is_valid=False,
        is_expired=False,
        user_id=None,
        username=None,
        role_name=None,
        message="Session tidak valid",
    )


@pytest.fixture
def expired_session_validation():
    """Expired SessionValidation untuk testing."""
    return SessionValidation(
        is_valid=False,
        is_expired=True,
        user_id=None,
        username=None,
        role_name=None,
        message="Session expired",
    )


@pytest.fixture
def sample_active_sessions():
    """Sample active sessions data untuk testing monitoring."""
    return [
        {
            "id": 1,
            "session_token": "token1",
            "user_id": 1,
            "username": "user1",
            "created_at": "2024-01-01T10:00:00",
            "last_activity": "2024-01-01T11:00:00",
            "ip_address": "192.168.1.100",
        },
        {
            "id": 2,
            "session_token": "token2",
            "user_id": 2,
            "username": "user2",
            "created_at": "2024-01-01T10:30:00",
            "last_activity": "2024-01-01T11:30:00",
            "ip_address": "192.168.1.101",
        },
    ]


# TODO: Add fixtures untuk SessionRepositoryORM integration tests
# TODO: Add fixtures untuk performance testing dengan large datasets
# REMINDER: Keep fixtures realistic dan representative dari actual usage
# PINNED: Consider adding parameterized fixtures untuk different test scenarios
