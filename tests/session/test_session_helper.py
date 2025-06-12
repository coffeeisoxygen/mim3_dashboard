"""Helper functions untuk test session_st.py backward compatibility."""

from unittest.mock import Mock, patch

from models.session.session_st import (
    clear_user_session,
    get_current_user,
    get_streamlit_context_debug,
    is_session_valid,
    set_user_session,
)


def patch_backward_compatibility():
    """Patch semua backward compatibility functions untuk test."""
    # Create mock untuk session manager singleton
    singleton_mock = Mock()
    singleton_mock.set_session.return_value = True
    singleton_mock.clear_session.return_value = True
    singleton_mock.is_authenticated.return_value = True
    singleton_mock.get_session_info.return_value = {
        "streamlit_id": "test_session",
        "user_id": 123,
        "username": "testuser",
        "authenticated": True,
        "role": "admin",
    }
    singleton_mock.get_context_summary.return_value = {
        "context_available": True,
        "features": {
            "ip_address": {"available": True, "has_value": True, "type": "str"},
            "headers": {"available": True, "has_value": True, "type": "dict"},
        },
        "session_id": "test_session",
    }

    # Patch singleton instance
    return patch("models.session.session_st._streamlit_session", singleton_mock)


def test_set_user_session_patched():
    """Test set_user_session dengan patching."""
    with patch_backward_compatibility():
        # Call should succeed
        result = set_user_session(Mock())
        assert result is True


def test_clear_user_session_patched():
    """Test clear_user_session dengan patching."""
    with patch_backward_compatibility():
        # Call should succeed
        result = clear_user_session()
        assert result is True


def test_get_current_user_patched():
    """Test get_current_user dengan patching."""
    with patch_backward_compatibility():
        # Call should return user info
        user_info = get_current_user()
        assert user_info["user_id"] == 123
        assert user_info["username"] == "testuser"
        assert user_info["authenticated"] is True


def test_is_session_valid_patched():
    """Test is_session_valid dengan patching."""
    with patch_backward_compatibility():
        # Call should return True
        result = is_session_valid()
        assert result is True


def test_get_streamlit_context_debug_patched():
    """Test get_streamlit_context_debug dengan patching."""
    with patch_backward_compatibility():
        # Call should return context info
        context_info = get_streamlit_context_debug()
        assert context_info["context_available"] is True
        assert context_info["session_id"] == "test_session"
        assert "features" in context_info


def test_backward_compatibility_error_handling():
    """Test error handling di backward compatibility functions."""
    # Override singleton dengan Mock that raises exceptions
    error_singleton = Mock()
    error_singleton.set_session.side_effect = Exception("Set session error")
    error_singleton.clear_session.side_effect = Exception("Clear session error")
    error_singleton.is_authenticated.side_effect = Exception("Auth error")
    error_singleton.get_session_info.side_effect = Exception("Session info error")
    error_singleton.get_context_summary.side_effect = Exception("Context error")

    with patch("models.session.session_st._streamlit_session", error_singleton):
        # Semua methods seharusnya handle error dengan elegan
        assert set_user_session(Mock()) is False
        assert clear_user_session() is False
        assert is_session_valid() is False

        user_info = get_current_user()
        assert isinstance(user_info, dict)
        assert "error" in user_info

        context_info = get_streamlit_context_debug()
        assert isinstance(context_info, dict)
        assert "error" in context_info
