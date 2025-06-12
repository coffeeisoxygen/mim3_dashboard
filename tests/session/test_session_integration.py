"""Integration tests untuk Streamlit session dengan komponen lain."""

from unittest.mock import Mock, patch

import pytest

from models.session.session_health import SessionHealthCheck
from models.session.session_st import (
    get_current_user,
    is_session_valid,
    set_user_session,
)


@pytest.fixture
def mock_session_data():
    """Fixture untuk mock session data."""
    data = Mock()
    data.user_id = 1
    data.username = "admin"
    data.display_name = "Admin User"
    data.role = "admin"
    data.session_token = "test_token_12345"
    return data


@pytest.fixture
def mock_session_state():
    """Fixture untuk mock session state."""
    return {}


class TestSessionStateInteractions:
    """Test interaksi session dengan Streamlit session state."""

    def test_session_state_persistence(self, mock_session_data, mock_session_state):
        """Test session state persistence after set_user_session."""
        with patch("streamlit.session_state", mock_session_state), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_1"):

            # Set session
            result = set_user_session(mock_session_data)
            assert result is True

            # Check state was set correctly
            assert mock_session_state["user_id"] == 1
            assert mock_session_state["username"] == "admin"
            assert mock_session_state["authenticated"] is True
            assert mock_session_state["user_role"] == "admin"

            # Check is_valid returns correct value
            assert is_session_valid() is True

            # Check user info
            user_info = get_current_user()
            assert user_info["authenticated"] is True
            assert user_info["user_id"] == 1


class TestSessionHealthIntegration:
    """Test integrasi session dengan health check system."""

    def test_session_health_integration(self, mock_session_state):
        """Test integrasi health check dengan session state."""
        # Prepare authenticated session
        mock_session_state["authenticated"] = True
        mock_session_state["user_id"] = 1
        mock_session_state["username"] = "admin"

        with patch("streamlit.session_state", mock_session_state), \
             patch("models.session.session_health.st.context", side_effect=Exception("No context")), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_1"):

            # Run health check
            health_report = SessionHealthCheck.run_full_health_check()

            # Even without context, session is valid so should return "degraded"
            assert health_report["overall_health"] == "degraded"
            assert health_report["session_state_health"]["session_state_available"] is True
            assert health_report["session_state_health"]["test_passed"] is True
            assert health_report["context_health"]["context_available"] is False


class TestSessionWithURLParameters:
    """Test integrasi session dengan URL parameters."""

    def test_session_with_query_params(self, mock_session_data, mock_session_state):
        """Test session integration dengan URL parameters."""
        # Mock query params
        mock_query_params = {"user": "admin", "view": "dashboard"}

        with patch("streamlit.session_state", mock_session_state), \
             patch("streamlit.query_params", mock_query_params), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_1"):

            # Set session
            set_user_session(mock_session_data)

            # Query params should be accessible
            user_info = get_current_user()
            assert user_info["user_id"] == 1
            assert user_info["username"] == "admin"

            # URL parameters should not affect session data
            assert mock_session_state["username"] == "admin"


class TestMultiPageSessionConsistency:
    """Test session konsistensi dalam multi-page setup."""

    def test_session_consistency_across_pages(self, mock_session_data, mock_session_state):
        """Test session konsistensi across multiple pages."""
        with patch("streamlit.session_state", mock_session_state), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_1"):

            # Set session on "login page"
            set_user_session(mock_session_data)

            # "Navigate" to another page by changing URL but keeping session state
            with patch("streamlit.context") as mock_context:
                mock_context.ip_address = "192.168.1.100"
                mock_context.url = "http://localhost:8501/dashboard" # Changed URL

                # Session should still be valid
                assert is_session_valid() is True

                # User data should persist
                user_info = get_current_user()
                assert user_info["username"] == "admin"
                assert user_info["authenticated"] is True


class TestSessionExpiry:
    """Test session expiry behavior."""

    def test_session_token_verification(self, mock_session_data, mock_session_state):
        """Test session dengan token verification."""
        with patch("streamlit.session_state", mock_session_state), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_1"):

            # Set session with token
            mock_session_data.session_token = "valid_token_123"
            set_user_session(mock_session_data)

            # Verify session is valid
            assert is_session_valid() is True

            # Change session token (simulate token expiry)
            mock_session_state["session_token"] = "expired_token_999"

            # Session still marked as authenticated in Streamlit
            assert mock_session_state["authenticated"] is True

            # But verification could check token validity externally
            user_info = get_current_user()
            assert user_info["session_token"] == "expired_token_999"


class TestRobustnessWithMultipleUsers:
    """Test robustness dengan multiple users."""

    def test_multiple_users_session_isolation(self):
        """Test isolation antara multiple user sessions."""
        # Create two separate session states
        session_state_1 = {}
        session_state_2 = {}

        # Create two users
        user1 = Mock()
        user1.user_id = 1
        user1.username = "user1"
        user1.display_name = "User One"
        user1.role = "user"
        user1.session_token = "token_1"

        user2 = Mock()
        user2.user_id = 2
        user2.username = "user2"
        user2.display_name = "User Two"
        user2.role = "admin"
        user2.session_token = "token_2"

        # Session for User 1
        with patch("streamlit.session_state", session_state_1), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="session_user1"):
            set_user_session(user1)

            # Verify User 1 session
            assert session_state_1["authenticated"] is True
            assert session_state_1["username"] == "user1"
            assert session_state_1["user_role"] == "user"

        # Session for User 2
        with patch("streamlit.session_state", session_state_2), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="session_user2"):
            set_user_session(user2)

            # Verify User 2 session
            assert session_state_2["authenticated"] is True
            assert session_state_2["username"] == "user2"
            assert session_state_2["user_role"] == "admin"

        # Verify sessions are isolated
        assert session_state_1["user_id"] == 1
        assert session_state_2["user_id"] == 2


# REMINDER: Integration tests verify components work together correctly
# PINNED: Session state adalah foundation untuk user state management
# TODO: Add real environment integration test dengan real Streamlit instance
# PINNED: Mocking streamlit APIs enables isolated testing
# TODO: Add security testing untuk session management
