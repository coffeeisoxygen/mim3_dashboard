"""Core unit tests untuk session_st.py - sesuai implementasi."""

import hashlib
from unittest.mock import Mock, patch

import pytest

from models.session.session_st import (
    StreamlitSessionManager,
    clear_user_session,
    get_current_user,
    is_session_valid,
    set_user_session,
)


@pytest.fixture
def mock_user_data():
    """Fixture untuk mock user data."""
    data = Mock()
    data.user_id = 123
    data.username = "testuser"
    data.display_name = "Test User"
    data.role = "admin"
    data.session_token = "test_token_123"
    return data


class TestStreamlitSessionID:
    """Test untuk streamlit_session_id property."""

    def test_session_id_with_context(self):
        """Test session ID generation normal case."""
        manager = StreamlitSessionManager()

        with patch("streamlit.context") as mock_context:
            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = {"user-agent": "TestBrowser"}
            mock_context.url = "http://localhost:8501/dashboard"

            # Metode ini menggunakan hash dari ketiga nilai tersebut
            expected_data = ["192.168.1.100", "TestBrowser", "localhost:8501/dashboard"]
            expected_hash = hashlib.sha256("|".join(expected_data).encode()).hexdigest()[:16]

            session_id = manager.streamlit_session_id

            assert session_id == expected_hash

            # Test consistency - ID yang sama untuk context yang sama
            session_id2 = manager.streamlit_session_id
            assert session_id == session_id2

    def test_session_id_fallback_to_timestamp(self):
        """Test fallback ke timestamp jika context kosong."""
        manager = StreamlitSessionManager()

        # Mock empty context_data list
        with patch("streamlit.context", side_effect=Exception("Context error")):
            with patch("time.time", return_value=12345):
                session_id = manager.streamlit_session_id

                # Seharusnya fallback ke timestamp-based
                assert session_id == "session_12345"

    def test_session_id_ultimate_fallback(self):
        """Test ultimate fallback jika semua gagal."""
        manager = StreamlitSessionManager()

        # Force exception di semua tahap
        with patch("streamlit.context", side_effect=Exception("Context error")), \
             patch("time.time", side_effect=Exception("Time error")):

            session_id = manager.streamlit_session_id

            # Ultimate fallback harus digunakan
            assert session_id == "local_session_default"


class TestSetSession:
    """Test untuk set_session method."""

    def test_set_session_normal_case(self, mock_user_data):
        """Test set session berhasil."""
        manager = StreamlitSessionManager()
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state), \
             patch.object(manager, "streamlit_session_id", return_value="test_session"):

            result = manager.set_session(mock_user_data)

            assert result is True
            assert mock_session_state["authenticated"] is True
            assert mock_session_state["user_id"] == 123
            assert mock_session_state["username"] == "testuser"
            assert mock_session_state["user_role"] == "admin"
            assert mock_session_state["session_id"] == "test_session"

    def test_set_session_clears_on_failure(self, mock_user_data):
        """Test set session membersihkan state jika gagal."""
        manager = StreamlitSessionManager()
        mock_session_state = {}

        # Trigger exception pada set user_role
        class BrokenSessionState(dict):
            def __setitem__(self, key, value):
                if key == "user_role":
                    raise Exception("Error setting attribute")
                super().__setitem__(key, value)

        broken_state = BrokenSessionState()

        with patch("streamlit.session_state", broken_state), \
             patch.object(manager, "streamlit_session_id", return_value="test_session"):

            # Panggil dengan broken state harus return False
            result = manager.set_session(mock_user_data)

            assert result is False

            # State seharusnya dibersihkan oleh clear_session()
            assert "authenticated" not in broken_state
            assert "user_id" not in broken_state


class TestClearSession:
    """Test untuk clear_session method."""

    def test_clear_session(self):
        """Test clear session menghapus semua key."""
        manager = StreamlitSessionManager()
        mock_session_state = {
            "authenticated": True,
            "user_id": 123,
            "username": "testuser",
            "display_name": "Test User",
            "user_role": "admin",
            "session_token": "token123",
            "session_id": "session123"
        }

        with patch("streamlit.session_state", mock_session_state):
            result = manager.clear_session()

            assert result is True

            # Semua key harus dihapus
            for key in ["authenticated", "user_id", "username", "display_name",
                       "user_role", "session_token", "session_id"]:
                assert key not in mock_session_state


class TestGetContextSummary:
    """Test untuk get_context_summary method."""

    def test_get_context_summary_normal(self):
        """Test get context summary dengan context normal."""
        manager = StreamlitSessionManager()

        with patch("streamlit.context") as mock_context, \
             patch.object(manager, "streamlit_session_id", return_value="test_session"):

            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = {"user-agent": "TestBrowser"}
            mock_context.url = "http://localhost:8501/"
            mock_context.locale = "id-ID"

            result = manager.get_context_summary()

            assert result["context_available"] is True
            assert result["session_id"] == "test_session"

            features = result["features"]
            assert features["ip_address"]["has_value"] is True
            assert features["headers"]["has_value"] is True
            assert features["url"]["has_value"] is True
            assert features["locale"]["has_value"] is True

    def test_get_context_summary_with_error(self):
        """Test get context summary dengan error."""
        manager = StreamlitSessionManager()

        with patch("streamlit.context", side_effect=Exception("Context error")), \
             patch.object(manager, "streamlit_session_id", return_value="test_session"):

            result = manager.get_context_summary()

            assert result["context_available"] is False
            assert result["session_id"] == "test_session"
            assert "context_error" in result
            assert "Context error" in result["context_error"]


class TestBackwardCompatibility:
    """Test untuk fungsi backward compatibility."""

    def test_set_user_session_calls_singleton(self, mock_user_data):
        """Test set_user_session memanggil singleton."""
        mock_session_state = {}

        with patch("models.session.session_st._streamlit_session.set_session") as mock_set_session, \
             patch("streamlit.session_state", mock_session_state):

            # Setup mock untuk return True
            mock_set_session.return_value = True

            result = set_user_session(mock_user_data)

            # Harus memanggil method pada singleton
            assert mock_set_session.called
            assert mock_set_session.call_args[0][0] == mock_user_data
            assert result is True

    def test_clear_user_session_calls_singleton(self):
        """Test clear_user_session memanggil singleton."""
        with patch("models.session.session_st._streamlit_session.clear_session") as mock_clear:
            # Setup mock return value
            mock_clear.return_value = True

            result = clear_user_session()

            # Harus memanggil method pada singleton
            assert mock_clear.called
            assert result is True

    def test_get_current_user_handles_error(self):
        """Test get_current_user dengan error."""
        with patch("models.session.session_st._streamlit_session.get_session_info",
                   side_effect=Exception("Session info error")):

            # Seharusnya tetap return dict dan tidak raise exception
            result = get_current_user()

            assert isinstance(result, dict)
            assert "error" in result
            assert not result.get("authenticated", False)

    def test_is_session_valid_handles_error(self):
        """Test is_session_valid dengan error."""
        with patch("models.session.session_st._streamlit_session.is_authenticated",
                   side_effect=Exception("Auth error")):

            # Seharusnya return False jika error
            assert is_session_valid() is False


if __name__ == "__main__":
    pytest.main(["-v", "test_session_core.py"])
