"""Unit tests untuk SessionService - comprehensive coverage."""

from unittest.mock import Mock, patch

import pytest

from models.session.session_db import SessionResult


class TestSessionServiceCreateSession:
    """Test cases untuk create_user_session method."""

    def test_create_session_success(
        self,
        session_service,
        mock_repository,
        sample_user_session,
        valid_session_result,
    ):
        """Test successful session creation."""
        # Arrange
        mock_repository.create_session.return_value = valid_session_result

        # Act
        with patch(
            "models.session.session_context.SessionContext.from_streamlit_context"
        ) as mock_context:
            mock_context.return_value = Mock(
                client_ip="192.168.1.100",
                user_agent="Mozilla/5.0 Test Browser",
                is_local_access=Mock(return_value=True),
                get_client_info=Mock(
                    return_value="IP: 192.168.1.100, Browser: Mozilla/5.0"
                ),
                get_display_timezone=Mock(return_value="Asia/Jakarta"),
            )

            result = session_service.create_user_session(sample_user_session)

        # Assert
        assert result.success is True
        assert result.token == "new_session_token"  # noqa: S105
        mock_repository.create_session.assert_called_once()

    def test_create_session_with_custom_context(
        self,
        session_service,
        mock_repository,
        sample_user_session,
        sample_session_context,
        valid_session_result,
    ):
        """Test session creation dengan custom context."""
        # Arrange
        mock_repository.create_session.return_value = valid_session_result

        # Act
        result = session_service.create_user_session(
            sample_user_session, sample_session_context
        )

        # Assert
        assert result.success is True
        mock_repository.create_session.assert_called_once()

        # Verify context was used in preparation
        call_args = mock_repository.create_session.call_args[0][0]  # SessionCreate
        assert call_args.ip_address == "192.168.1.100"
        assert call_args.user_agent == "Mozilla/5.0 Test Browser"

    def test_create_session_repository_failure(
        self, session_service, mock_repository, sample_user_session
    ):
        """Test handling repository failure."""
        # Arrange
        failed_result = SessionResult(
            success=False, message="Database error", session_id=None, token=None
        )
        mock_repository.create_session.return_value = failed_result

        # Act
        with patch(
            "models.session.session_context.SessionContext.from_streamlit_context"
        ):
            result = session_service.create_user_session(sample_user_session)

        # Assert
        assert result.success is False
        assert result.message == "Database error"

    def test_create_session_exception_handling(
        self, session_service, mock_repository, sample_user_session
    ):
        """Test exception handling dalam create_session."""
        # Arrange
        mock_repository.create_session.side_effect = Exception(
            "Database connection error"
        )

        # Act
        with patch(
            "models.session.session_context.SessionContext.from_streamlit_context"
        ):
            result = session_service.create_user_session(sample_user_session)

        # Assert
        assert result.success is False
        assert "Error sistem" in result.message

    def test_prepare_session_with_context_string_validation(
        self, session_service, sample_user_session
    ):
        """Test string validation dalam _prepare_session_with_context."""
        # Arrange - Context dengan long strings
        long_context = Mock(
            client_ip="very.long.ip.address.that.exceeds.normal.length.limit.test",
            user_agent="very" * 200,  # Very long user agent
        )

        # Act
        session_data = session_service._prepare_session_with_context(
            sample_user_session, long_context
        )

        # Assert - Strings should be truncated
        assert len(session_data.ip_address) <= 45
        assert len(session_data.user_agent) <= 500

    def test_prepare_session_with_none_context_values(
        self, session_service, sample_user_session
    ):
        """Test handling None values dalam context."""
        # Arrange
        none_context = Mock(client_ip=None, user_agent=None)

        # Act
        session_data = session_service._prepare_session_with_context(
            sample_user_session, none_context
        )

        # Assert
        assert session_data.ip_address is None
        assert session_data.user_agent is None


class TestSessionServiceValidation:
    """Test cases untuk session validation methods."""

    def test_validate_session_success(
        self, session_service, mock_repository, valid_session_validation
    ):
        """Test successful session validation."""
        # Arrange
        mock_repository.get_session_by_token.return_value = valid_session_validation

        # Act
        result = session_service.validate_session("valid_token")

        # Assert
        assert result.is_valid is True
        assert result.user_id == 1
        assert result.username == "test_user"
        mock_repository.get_session_by_token.assert_called_once_with("valid_token")

    def test_validate_session_no_token(self, session_service):
        """Test validation dengan token None."""
        # Act
        result = session_service.validate_session(None)

        # Assert
        assert result.is_valid is False
        assert "Token tidak ada" in result.message

    def test_validate_session_empty_token(self, session_service):
        """Test validation dengan empty string token."""
        # Act
        result = session_service.validate_session("")

        # Assert
        assert result.is_valid is False
        assert "Token tidak ada" in result.message

    def test_refresh_session_success(self, session_service, mock_repository):
        """Test successful session refresh."""
        # Arrange
        mock_repository.is_session_expired.return_value = False
        mock_repository.update_session_activity.return_value = True

        # Act
        result = session_service.refresh_session("valid_token")

        # Assert
        assert result is True
        mock_repository.is_session_expired.assert_called_once_with("valid_token")
        mock_repository.update_session_activity.assert_called_once_with("valid_token")

    def test_refresh_session_expired(self, session_service, mock_repository):
        """Test refresh pada expired session."""
        # Arrange
        mock_repository.is_session_expired.return_value = True

        # Act
        result = session_service.refresh_session("expired_token")

        # Assert
        assert result is False
        mock_repository.is_session_expired.assert_called_once_with("expired_token")
        mock_repository.update_session_activity.assert_not_called()

    def test_refresh_session_activity_update_failed(
        self, session_service, mock_repository
    ):
        """Test refresh ketika activity update gagal."""
        # Arrange
        mock_repository.is_session_expired.return_value = False
        mock_repository.update_session_activity.return_value = False

        # Act
        result = session_service.refresh_session("valid_token")

        # Assert
        assert result is False


class TestSessionServiceAdmin:
    """Test cases untuk admin functions."""

    def test_force_logout_user_success(self, session_service, mock_repository):
        """Test successful force logout."""
        # Arrange
        mock_repository.force_deactivate_user_sessions.return_value = True

        # Act
        result = session_service.force_logout_user(1)

        # Assert
        assert result is True
        mock_repository.force_deactivate_user_sessions.assert_called_once_with(1)

    def test_force_logout_user_failure(self, session_service, mock_repository):
        """Test force logout failure."""
        # Arrange
        mock_repository.force_deactivate_user_sessions.return_value = False

        # Act
        result = session_service.force_logout_user(1)

        # Assert
        assert result is False

    def test_get_active_sessions_success(self, session_service, mock_repository):
        """Test getting active sessions."""
        # Arrange
        mock_sessions = [
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
        mock_repository.get_active_sessions.return_value = mock_sessions

        # Act
        result = session_service.get_active_sessions_for_monitoring()

        # Assert
        assert len(result) == 2
        assert result[0]["username"] == "user1"
        assert result[1]["user_id"] == 2
        mock_repository.get_active_sessions.assert_called_once_with(None)

    def test_get_active_sessions_filtered_by_user(
        self, session_service, mock_repository
    ):
        """Test getting active sessions filtered by user."""
        # Arrange
        mock_sessions = [
            {
                "id": 1,
                "session_token": "token1",
                "user_id": 1,
                "username": "user1",
                "created_at": "2024-01-01T10:00:00",
                "last_activity": "2024-01-01T11:00:00",
                "ip_address": "192.168.1.100",
            }
        ]
        mock_repository.get_active_sessions.return_value = mock_sessions

        # Act
        result = session_service.get_active_sessions_for_monitoring(user_id=1)

        # Assert
        assert len(result) == 1
        assert result[0]["user_id"] == 1
        mock_repository.get_active_sessions.assert_called_once_with(1)

    def test_get_active_sessions_empty_result(self, session_service, mock_repository):
        """Test getting active sessions dengan empty result."""
        # Arrange
        mock_repository.get_active_sessions.return_value = []

        # Act
        result = session_service.get_active_sessions_for_monitoring()

        # Assert
        assert len(result) == 0
        assert result == []


class TestSessionServiceEdgeCases:
    """Test edge cases dan error scenarios."""

    def test_create_session_with_context_extraction_failure(
        self,
        session_service,
        mock_repository,
        sample_user_session,
        valid_session_result,
    ):
        """Test session creation ketika context extraction gagal."""
        # Arrange
        mock_repository.create_session.return_value = valid_session_result

        # Act
        with patch(
            "models.session.session_context.SessionContext.from_streamlit_context"
        ) as mock_context:
            mock_context.side_effect = Exception("Context extraction failed")

            result = session_service.create_user_session(sample_user_session)

        # Assert
        assert result.success is False
        assert "Error sistem" in result.message

    def test_validate_session_with_repository_exception(
        self, session_service, mock_repository
    ):
        """Test validation ketika repository raise exception."""
        # Arrange
        mock_repository.get_session_by_token.side_effect = Exception("DB error")

        # Act & Assert
        with pytest.raises(Exception):  # noqa: B017
            session_service.validate_session("valid_token")

    def test_refresh_session_with_repository_exception(
        self, session_service, mock_repository
    ):
        """Test refresh ketika repository raise exception."""
        # Arrange
        mock_repository.is_session_expired.side_effect = Exception("DB error")

        # Act & Assert
        with pytest.raises(Exception):  # noqa: B017
            session_service.refresh_session("valid_token")


# REMINDER: Add integration tests dengan real SessionRepositoryORM
# TODO: Add performance tests untuk session creation dengan large context
# PINNED: Consider adding tests untuk concurrent session operations
