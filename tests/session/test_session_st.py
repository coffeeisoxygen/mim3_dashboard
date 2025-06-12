"""Unit tests untuk Streamlit session management."""

from unittest.mock import Mock, patch

import pytest

from models.session.session_st import (
    StreamlitSessionManager,
    clear_user_session,
    get_current_user,
    get_streamlit_context_debug,
    is_session_valid,
    set_user_session,
)


@pytest.fixture
def mock_user_data():
    """Fixture untuk mock user data."""
    mock_data = Mock()
    mock_data.user_id = 123
    mock_data.username = "testuser"
    mock_data.display_name = "Test User"
    mock_data.role = "admin"
    mock_data.session_token = "test_token_123"
    return mock_data


@pytest.fixture
def session_manager():
    """Fixture untuk StreamlitSessionManager instance."""
    return StreamlitSessionManager()


@pytest.fixture
def mock_streamlit_context():
    """Fixture untuk mock streamlit context."""
    mock_context = Mock()
    mock_context.ip_address = "192.168.1.100"
    mock_context.headers = {"user-agent": "Mozilla/5.0 Test Browser"}
    mock_context.url = "http://localhost:8501/dashboard"
    mock_context.timezone = "Asia/Jakarta"
    mock_context.timezone_offset = 25200
    mock_context.locale = "id"
    mock_context.cookies = {"session": "test123"}
    mock_context.is_embedded = False
    return mock_context


@pytest.fixture
def mock_session_state():
    """Fixture untuk mock session state."""
    # Dictionary-like object untuk simulate st.session_state
    class MockSessionState(dict):
        pass

    return MockSessionState()


class TestStreamlitSessionId:
    """Tests untuk streamlit_session_id property."""

    def test_session_id_generation_with_full_context(self, session_manager):
        """Test session ID generation dengan context yang lengkap."""
        with patch("streamlit.context") as mock_context:
            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = {"user-agent": "TestBrowser/1.0"}
            mock_context.url = "http://localhost:8501/dashboard"

            # Generate session ID
            session_id = session_manager.streamlit_session_id

            # ID harus konsisten untuk context yang sama
            assert isinstance(session_id, str)
            assert len(session_id) == 16

            # Check consistency - should generate same ID for same context
            session_id_2 = session_manager.streamlit_session_id
            assert session_id == session_id_2

    def test_session_id_generation_with_partial_context(self, session_manager):
        """Test session ID generation dengan partial context."""
        with patch("streamlit.context") as mock_context:
            mock_context.ip_address = "192.168.1.100"
            # Missing headers and URL
            mock_context.headers = None
            mock_context.url = None

            # Should still generate a valid session ID
            session_id = session_manager.streamlit_session_id

            assert isinstance(session_id, str)
            assert len(session_id) == 16

    def test_session_id_generation_with_failed_context(self, session_manager):
        """Test session ID generation ketika context gagal access."""
        with patch("streamlit.context", side_effect=RuntimeError("Context not available")):
            # Should fall back to timestamp-based or default ID
            session_id = session_manager.streamlit_session_id

            assert isinstance(session_id, str)
            assert session_id == "local_session_default" or session_id.startswith("session_")

    def test_session_id_generation_with_different_contexts(self, session_manager):
        """Test session ID berbeda untuk context berbeda."""
        with patch("streamlit.context") as mock_context:
            # Context 1
            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = {"user-agent": "TestBrowser/1.0"}
            mock_context.url = "http://localhost:8501/dashboard"

            session_id_1 = session_manager.streamlit_session_id

            # Context 2 - different IP
            mock_context.ip_address = "192.168.1.101"

            session_id_2 = session_manager.streamlit_session_id

            # Different contexts should produce different IDs
            assert session_id_1 != session_id_2


class TestSetSession:
    """Tests untuk set_session method."""

    def test_set_session_success(self, session_manager, mock_user_data, mock_session_state):
        """Test set session berhasil."""
        with patch("streamlit.session_state", mock_session_state), \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            result = session_manager.set_session(mock_user_data)

            assert result is True
            assert mock_session_state["authenticated"] is True
            assert mock_session_state["user_id"] == mock_user_data.user_id
            assert mock_session_state["username"] == mock_user_data.username
            assert mock_session_state["display_name"] == mock_user_data.display_name
            assert mock_session_state["user_role"] == mock_user_data.role
            assert mock_session_state["session_token"] == mock_user_data.session_token
            assert mock_session_state["session_id"] == "test_session_id"

    def test_set_session_with_none_data(self, session_manager, mock_session_state):
        """Test set session dengan data None."""
        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.set_session(None)

            assert result is False
            assert "authenticated" not in mock_session_state

    def test_set_session_with_exception(self, session_manager, mock_user_data, mock_session_state):
        """Test set session dengan exception."""
        with patch("streamlit.session_state", mock_session_state), \
             patch.object(session_manager, "streamlit_session_id", side_effect=Exception("Test error")):

            # Should handle exception and return False
            result = session_manager.set_session(mock_user_data)

            assert result is False


class TestClearSession:
    """Tests untuk clear_session method."""

    def test_clear_session_with_data(self, session_manager, mock_session_state):
        """Test clear session ketika ada data."""
        mock_session_state["authenticated"] = True
        mock_session_state["user_id"] = 123
        mock_session_state["username"] = "testuser"
        mock_session_state["display_name"] = "Test User"
        mock_session_state["user_role"] = "admin"
        mock_session_state["session_token"] = "test_token"
        mock_session_state["session_id"] = "test_session_id"

        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.clear_session()

            assert result is True
            assert "authenticated" not in mock_session_state
            assert "user_id" not in mock_session_state
            assert "username" not in mock_session_state
            assert "display_name" not in mock_session_state
            assert "user_role" not in mock_session_state
            assert "session_token" not in mock_session_state
            assert "session_id" not in mock_session_state

    def test_clear_session_with_empty_state(self, session_manager, mock_session_state):
        """Test clear session ketika session kosong."""
        # Start with empty session
        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.clear_session()

            assert result is True  # Should still return True


class TestGetSessionInfo:
    """Tests untuk get_session_info method."""

    def test_get_session_info_with_full_data(self, session_manager, mock_session_state, mock_streamlit_context):
        """Test get session info dengan data lengkap."""
        # Setup session state
        mock_session_state["authenticated"] = True
        mock_session_state["user_id"] = 123
        mock_session_state["username"] = "testuser"
        mock_session_state["display_name"] = "Test User"
        mock_session_state["user_role"] = "admin"
        mock_session_state["session_token"] = "test_token"

        with patch("streamlit.session_state", mock_session_state), \
             patch("streamlit.context", mock_streamlit_context), \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            info = session_manager.get_session_info()

            # Check session data
            assert info["streamlit_id"] == "test_session_id"
            assert info["user_id"] == 123
            assert info["username"] == "testuser"
            assert info["display_name"] == "Test User"
            assert info["role"] == "admin"
            assert info["authenticated"] is True
            assert info["session_token"] == "test_token"

            # Check context enrichment
            assert info["client_ip"] == "192.168.1.100"
            assert info["access_url"] == "http://localhost:8501/dashboard"
            assert info["timezone"] == "Asia/Jakarta"
            assert info["locale"] == "id"
            assert info["is_embedded"] is False

    def test_get_session_info_with_empty_state(self, session_manager, mock_session_state):
        """Test get session info dengan state kosong."""
        with patch("streamlit.session_state", mock_session_state), \
             patch("streamlit.context", side_effect=AttributeError("Context not available")), \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            info = session_manager.get_session_info()

            # Basic session info should still be included, but with None values
            assert info["streamlit_id"] == "test_session_id"
            assert info["user_id"] is None
            assert info["username"] is None
            assert info["display_name"] is None
            assert info["role"] is None
            assert info["authenticated"] is False
            assert info["session_token"] is None

            # Context enrichment should be skipped without errors


class TestIsAuthenticated:
    """Tests untuk is_authenticated method."""

    def test_is_authenticated_true(self, session_manager, mock_session_state):
        """Test is_authenticated dengan user terauthentikasi."""
        mock_session_state["authenticated"] = True

        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.is_authenticated()

            assert result is True

    def test_is_authenticated_false(self, session_manager, mock_session_state):
        """Test is_authenticated dengan user tidak terauthentikasi."""
        # No authenticated flag
        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.is_authenticated()

            assert result is False

    def test_is_authenticated_explicitly_false(self, session_manager, mock_session_state):
        """Test is_authenticated dengan flag explicitly False."""
        mock_session_state["authenticated"] = False

        with patch("streamlit.session_state", mock_session_state):
            result = session_manager.is_authenticated()

            assert result is False


class TestGetContextSummary:
    """Tests untuk get_context_summary method."""

    def test_get_context_summary_with_full_context(self, session_manager, mock_streamlit_context):
        """Test get context summary dengan context lengkap."""
        with patch("streamlit.context", mock_streamlit_context), \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            summary = session_manager.get_context_summary()

            assert summary["context_available"] is True
            assert summary["session_id"] == "test_session_id"

            features = summary["features"]
            assert features["ip_address"]["available"] is True
            assert features["ip_address"]["has_value"] is True
            assert features["ip_address"]["type"] == "str"

            assert features["headers"]["available"] is True
            assert features["headers"]["has_value"] is True
            assert features["headers"]["type"] == "dict"

            assert features["url"]["available"] is True
            assert features["url"]["has_value"] is True
            assert features["url"]["type"] == "str"

    def test_get_context_summary_with_missing_features(self, session_manager):
        """Test get context summary dengan sebagian features missing."""
        with patch("streamlit.context") as mock_context, \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            # Only set some features
            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = None  # Missing
            mock_context.url = "http://localhost:8501"

            summary = session_manager.get_context_summary()

            assert summary["context_available"] is True
            features = summary["features"]

            assert features["ip_address"]["available"] is True
            assert features["ip_address"]["has_value"] is True

            assert features["headers"]["available"] is True
            assert features["headers"]["has_value"] is False
            assert features["headers"]["type"] == "None"

            assert features["url"]["available"] is True
            assert features["url"]["has_value"] is True

    def test_get_context_summary_with_context_error(self, session_manager):
        """Test get context summary ketika context access error."""
        with patch("streamlit.context", side_effect=RuntimeError("Context not available")), \
             patch.object(session_manager, "streamlit_session_id", return_value="test_session_id"):

            summary = session_manager.get_context_summary()

            assert summary["context_available"] is False
            assert summary["session_id"] == "test_session_id"
            assert "context_error" in summary
            assert "Context not available" in summary["context_error"]


class TestBackwardCompatibilityAPI:
    """Tests untuk backward compatibility API functions."""

    def test_set_user_session(self, mock_user_data, mock_session_state):
        """Test set_user_session backward compatibility function."""
        with patch("streamlit.session_state", mock_session_state), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_id"):

            result = set_user_session(mock_user_data)

            assert result is True
            assert mock_session_state["authenticated"] is True
            assert mock_session_state["user_id"] == mock_user_data.user_id
            assert mock_session_state["username"] == mock_user_data.username

    def test_clear_user_session(self, mock_session_state):
        """Test clear_user_session backward compatibility function."""
        mock_session_state["authenticated"] = True
        mock_session_state["user_id"] = 123

        with patch("streamlit.session_state", mock_session_state):
            result = clear_user_session()

            assert result is True
            assert "authenticated" not in mock_session_state
            assert "user_id" not in mock_session_state

    def test_get_current_user(self, mock_session_state, mock_streamlit_context):
        """Test get_current_user backward compatibility function."""
        mock_session_state["authenticated"] = True
        mock_session_state["user_id"] = 123
        mock_session_state["username"] = "testuser"

        with patch("streamlit.session_state", mock_session_state), \
             patch("streamlit.context", mock_streamlit_context), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_id"):

            user_info = get_current_user()

            assert user_info["user_id"] == 123
            assert user_info["username"] == "testuser"
            assert user_info["authenticated"] is True
            assert user_info["streamlit_id"] == "test_session_id"

    def test_is_session_valid(self, mock_session_state):
        """Test is_session_valid backward compatibility function."""
        mock_session_state["authenticated"] = True

        with patch("streamlit.session_state", mock_session_state):
            result = is_session_valid()

            assert result is True

        # Test invalid session
        mock_session_state.clear()
        with patch("streamlit.session_state", mock_session_state):
            result = is_session_valid()

            assert result is False

    def test_get_streamlit_context_debug(self, mock_streamlit_context):
        """Test get_streamlit_context_debug backward compatibility function."""
        with patch("streamlit.context", mock_streamlit_context), \
             patch("models.session.session_st._streamlit_session.streamlit_session_id", return_value="test_session_id"):

            context_debug = get_streamlit_context_debug()

            assert context_debug["context_available"] is True
            assert context_debug["session_id"] == "test_session_id"
            assert "features" in context_debug
            assert context_debug["features"]["ip_address"]["has_value"] is True


# REMINDER: mock _streamlit_session singleton untuk test stability
# PINNED: Session ID consistency test penting untuk LAN deployment
# TODO: Add integration test dengan real Streamlit environment
# PINNED: Full mocking untuk isolasi dari framework
