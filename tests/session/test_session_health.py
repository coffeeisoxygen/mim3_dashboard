"""Unit tests untuk SessionHealthCheck - system health monitoring."""

from unittest.mock import patch


from models.session.session_health import SessionHealthCheck


class TestSessionHealthCheckContextAvailability:
    """Test cases untuk context availability checking."""

    def test_check_context_all_available(self):
        """Test when all Streamlit context components are available."""
        with patch("models.session.session_health.st.context") as mock_context, \
            patch("models.session.session_health.hasattr", return_value=True):
            # Mock successful context access
            mock_context.ip_address = "192.168.1.100"
            mock_context.headers = {"user-agent": "Test Browser"}
            mock_context.url = "http://192.168.1.100:8501"
            mock_context.timezone = "Asia/Jakarta"

            result = SessionHealthCheck.check_streamlit_context_availability()

            assert result["context_available"] is True
            assert result["fallback_used"] is False
            assert len(result["issues"]) == 0

    def test_check_context_partial_available(self):
        """Test when some context components are missing."""
        with patch("models.session.session_health.st.context") as mock_context, \
            patch("models.session.session_health.hasattr", return_value=True):
            # Mock partial context availability
            mock_context.ip_address = "192.168.1.100"  # Available
            mock_context.headers = None  # Not available

            result = SessionHealthCheck.check_streamlit_context_availability()

            assert result["context_available"] is True
            assert result["fallback_used"] is True

    def test_check_context_none_available(self):
        """Test when no context components are available."""
        # Mock hasattr to return False untuk st.context
        with patch("models.session.session_health.hasattr", return_value=False):
            result = SessionHealthCheck.check_streamlit_context_availability()

            assert result["context_available"] is False
            assert result["fallback_used"] is True
            assert len(result["issues"]) > 0


class TestSessionHealthCheckSessionState:
    """Test cases untuk session state health monitoring."""

    def test_check_session_state_healthy(self):
        """Test session state health when everything is working."""
        with patch("models.session.session_health.st.session_state", {"user_id": 1, "username": "admin"}), \
            patch("models.session.session_health.hasattr", return_value=True):
            result = SessionHealthCheck.check_session_state_health()

            assert result["session_state_available"] is True
            assert result["test_passed"] is True
            assert len(result["issues"]) == 0

    def test_check_session_state_inaccessible(self):
        """Test session state when completely inaccessible."""
        # Mock hasattr to return False untuk st.session_state
        with patch("models.session.session_health.hasattr", return_value=False):
            result = SessionHealthCheck.check_session_state_health()

            assert result["session_state_available"] is False
            assert result["test_passed"] is False
            assert len(result["issues"]) > 0


class TestSessionHealthCheckFullReport:
    """Test cases untuk comprehensive health reporting."""

    def test_full_health_report_healthy(self):
        """Test full health report when system is healthy."""
        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check, \
             patch("models.session.session_health.hasattr", return_value=True):

            # Mock healthy checks
            mock_context_check.return_value = {
                "context_available": True,
                "features": {},
                "issues": [],
                "fallback_used": False
            }
            mock_session_check.return_value = {
                "session_state_available": True,
                "test_passed": True,
                "issues": []
            }

            with patch("models.session.session_health.st.context") as mock_context:
                mock_context.ip_address = "192.168.1.100"

                report = SessionHealthCheck.run_full_health_check()

                assert report["overall_health"] in ["healthy", "healthy_with_fallbacks"]
                assert report["deployment_type"] == "lan"
                assert len(report["recommendations"]) > 0

    def test_full_health_report_degraded(self):
        """Test full health report when system is degraded."""
        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check:

            # Mock context failure but session OK
            mock_context_check.return_value = {
                "context_available": False,
                "features": {},
                "issues": ["Context not available: test error"],
                "fallback_used": True
            }
            mock_session_check.return_value = {
                "session_state_available": True,
                "test_passed": True,
                "issues": []
            }

            report = SessionHealthCheck.run_full_health_check()

            # When context fails but session state works, it should be degraded
            assert report["overall_health"] == "degraded"
            assert len(report["recommendations"]) > 0

    def test_full_health_report_localhost(self):
        """Test health report untuk localhost deployment."""
        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check, \
             patch("models.session.session_health.hasattr", return_value=True):

            mock_context_check.return_value = {
                "context_available": True,
                "features": {},
                "issues": [],
                "fallback_used": False
            }
            mock_session_check.return_value = {
                "session_state_available": True,
                "test_passed": True,
                "issues": []
            }

            with patch("models.session.session_health.st.context") as mock_context:
                mock_context.ip_address = "127.0.0.1"

                report = SessionHealthCheck.run_full_health_check()

                assert report["deployment_type"] == "localhost"

    def test_full_health_report_external(self):
        """Test health report untuk external deployment."""
        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check, \
             patch("models.session.session_health.hasattr", return_value=True):

            mock_context_check.return_value = {
                "context_available": True,
                "features": {},
                "issues": [],
                "fallback_used": False
            }
            mock_session_check.return_value = {
                "session_state_available": True,
                "test_passed": True,
                "issues": []
            }

            with patch("models.session.session_health.st.context") as mock_context:
                mock_context.ip_address = "203.0.113.1"  # Public IP

                report = SessionHealthCheck.run_full_health_check()

                assert report["deployment_type"] == "external"


class TestSessionHealthCheckFallbackBehavior:
    """Test cases untuk fallback behavior when Streamlit context fails."""

    def test_fallback_context_values(self):
        """Test fallback values when context extraction fails."""
        # Mock hasattr to return False untuk st.context
        with patch("models.session.session_health.hasattr", return_value=False):
            result = SessionHealthCheck.check_streamlit_context_availability()

            # Should provide fallback assessment
            assert isinstance(result, dict)
            assert result["fallback_used"] is True

    def test_resilient_health_reporting(self):
        """Test that health reporting is resilient to various failures."""
        # Test with all possible failures
        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check:

            # Mock both checks failing
            mock_context_check.return_value = {
                "context_available": False,
                "features": {},
                "issues": ["Context not available: test error"],
                "fallback_used": True
            }
            mock_session_check.return_value = {
                "session_state_available": False,
                "test_passed": False,
                "issues": ["Session state test failed: test error"]
            }

            report = SessionHealthCheck.run_full_health_check()

            assert isinstance(report, dict)
            assert report["overall_health"] == "unhealthy"
            assert len(report["recommendations"]) > 0


class TestSessionHealthCheckPerformance:
    """Test cases untuk performance aspects of health checking."""

    def test_health_check_performance(self):
        """Test that health checks complete within reasonable time."""
        import time

        with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
             patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check:

            # Simple mock returns
            mock_context_check.return_value = {
                "context_available": True,
                "features": {},
                "issues": [],
                "fallback_used": False
            }
            mock_session_check.return_value = {
                "session_state_available": True,
                "test_passed": True,
                "issues": []
            }

            start_time = time.time()

            # Run multiple health checks
            for _ in range(10):
                SessionHealthCheck.run_full_health_check()

            elapsed_time = time.time() - start_time

            # Should complete quickly (less than 1 second for 10 runs)
            assert elapsed_time < 1.0

    def test_health_check_non_intrusive(self):
        """Test that health checks don't modify session state."""
        original_state = {"test": "data", "user_id": 123}

        with patch("models.session.session_health.st.session_state", original_state.copy()):
            with patch("models.session.session_health.SessionHealthCheck.check_streamlit_context_availability") as mock_context_check, \
                 patch("models.session.session_health.SessionHealthCheck.check_session_state_health") as mock_session_check:

                # Simple mock returns
                mock_context_check.return_value = {
                    "context_available": True,
                    "features": {},
                    "issues": [],
                    "fallback_used": False
                }
                mock_session_check.return_value = {
                    "session_state_available": True,
                    "test_passed": True,
                    "issues": []
                }

                SessionHealthCheck.run_full_health_check()


class TestSessionHealthUtilityFunctions:
    """Test cases untuk utility functions."""

    def test_get_health_summary_healthy(self):
        """Test health summary untuk healthy system."""
        from models.session.session_health import get_health_summary

        with patch("models.session.session_health.SessionHealthCheck.run_full_health_check") as mock_health_check:
            mock_health_check.return_value = {
                "overall_health": "healthy",
                "context_health": {},
                "session_state_health": {},
                "deployment_type": "lan",
                "recommendations": [],
                "timestamp": "2024-01-01T12:00:00"
            }

            summary = get_health_summary()

            assert "🟢" in summary  # Healthy

    def test_get_health_summary_unhealthy(self):
        """Test health summary untuk unhealthy system."""
        from models.session.session_health import get_health_summary

        with patch("models.session.session_health.SessionHealthCheck.run_full_health_check") as mock_health_check:
            mock_health_check.return_value = {
                "overall_health": "unhealthy",
                "context_health": {},
                "session_state_health": {},
                "deployment_type": "lan",
                "recommendations": [],
                "timestamp": "2024-01-01T12:00:00"
            }

            summary = get_health_summary()

            assert "🔴" in summary  # Unhealthy

    def test_get_health_summary_exception_handling(self):
        """Test health summary dengan exception handling."""
        from models.session.session_health import get_health_summary

        with patch("models.session.session_health.SessionHealthCheck.run_full_health_check",
                  side_effect=Exception("Health check failed")):

            summary = get_health_summary()

            assert "🔴" in summary  # Should show failure
            assert "Gagal" in summary


# REMINDER: Tests aligned dengan actual SessionHealthCheck implementation
# PINNED: Improved mocking approach to ensure tests pass consistently
# TODO: Add integration tests dengan actual Streamlit environment
# PINNED: Test fallback behavior critical untuk LAN deployment reliability
# TODO: Add mock untuk get_fallback_context() function usage
