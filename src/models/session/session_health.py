"""Session system health monitoring dengan production fallbacks."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

import streamlit as st
from loguru import logger

from .session_config import get_fallback_context


class ContextHealthReport(TypedDict):
    """Type structure untuk context health report."""

    context_available: bool
    features: dict[str, Any]
    issues: list[str]
    fallback_used: bool


class SessionStateHealthReport(TypedDict):
    """Type structure untuk session state health report."""

    session_state_available: bool
    test_passed: bool
    issues: list[str]


class FullHealthReport(TypedDict):
    """Type structure untuk full health report."""

    timestamp: str
    overall_health: str
    context_health: ContextHealthReport
    session_state_health: SessionStateHealthReport
    deployment_type: str
    recommendations: list[str]


class SessionHealthCheck:
    """Monitor session system health dengan production awareness."""

    @staticmethod
    def check_streamlit_context_availability() -> ContextHealthReport:
        """Check available Streamlit context features dengan fallback awareness."""
        health: ContextHealthReport = {
            "context_available": False,
            "features": {},
            "issues": [],
            "fallback_used": False,
        }

        try:
            # Test basic context access - gunakan getattr untuk handle jika st.context tidak ada
            if not hasattr(st, "context"):
                raise AttributeError("st.context is not available")

            # Akses st.context untuk memastikan tidak ada exception
            _ = st.context
            health["context_available"] = True

            # Test individual features
            features_to_test = [
                "ip_address",
                "headers",
                "url",
                "timezone",
                "timezone_offset",
                "locale",
                "cookies",
            ]

            features_dict = health["features"]
            issues_list = health["issues"]
            fallback_values = get_fallback_context()

            for feature in features_to_test:
                try:
                    value = getattr(st.context, feature, None)

                    if value is not None:
                        features_dict[feature] = {
                            "available": True,
                            "has_value": True,
                            "type": type(value).__name__,
                            "fallback_needed": False,
                        }
                    else:
                        # Value is None - fallback will be used
                        health["fallback_used"] = True
                        features_dict[feature] = {
                            "available": True,
                            "has_value": False,
                            "type": "NoneType",
                            "fallback_needed": True,
                            "fallback_value": fallback_values.get(feature, "N/A"),
                        }

                except Exception as e:
                    health["fallback_used"] = True
                    features_dict[feature] = {
                        "available": False,
                        "error": str(e),
                        "fallback_needed": True,
                        "fallback_value": fallback_values.get(feature, "N/A"),
                    }
                    issues_list.append(f"Feature {feature} not available: {e}")

        except Exception as e:
            # If basic context access fails, mark as unavailable
            health["context_available"] = False
            health["fallback_used"] = True
            issues_list = health["issues"]
            issues_list.append(f"Context not available: {e}")

        return health

    @staticmethod
    def check_session_state_health() -> SessionStateHealthReport:
        """Check session state functionality."""
        health: SessionStateHealthReport = {
            "session_state_available": False,
            "test_passed": False,
            "issues": [],
        }

        try:
            # Test basic session state access first
            if not hasattr(st, "session_state"):
                raise AttributeError("st.session_state is not available")

            test_key = "_health_check_test"

            # Try to access session state
            _ = st.session_state
            health["session_state_available"] = True

            # Try to write to session state
            try:
                st.session_state[test_key] = "test_value"

                if st.session_state.get(test_key) == "test_value":
                    health["test_passed"] = True

                # Cleanup
                st.session_state.pop(test_key, None)
            except Exception as e:
                issues_list = health["issues"]
                issues_list.append(f"Session state write test failed: {e}")
                health["test_passed"] = False

        except Exception as e:
            # When session state fails, mark as unavailable
            health["session_state_available"] = False
            health["test_passed"] = False
            issues_list = health["issues"]
            issues_list.append(f"Session state test failed: {e}")

        return health

    @staticmethod
    def run_full_health_check() -> FullHealthReport:
        """Run comprehensive session health check dengan recommendations."""
        logger.info("Running session system health check")

        context_health = SessionHealthCheck.check_streamlit_context_availability()
        session_health = (
            SessionHealthCheck.check_session_state_health()
        )  # Determine deployment type
        deployment_type = "unknown"
        try:
            # Fixed: Check context availability first
            if not context_health["context_available"]:
                deployment_type = "localhost"  # Default when context unavailable
            elif (
                hasattr(st, "context")
                and hasattr(st.context, "ip_address")
                and st.context.ip_address
            ):
                ip = st.context.ip_address
                if ip in {"127.0.0.1", "::1"}:
                    deployment_type = "localhost"
                elif ip.startswith("192.168."):
                    deployment_type = "lan"
                else:
                    deployment_type = "external"
            else:
                deployment_type = "localhost"  # Default assumption
        except Exception as e:
            logger.warning("Could not determine deployment type: {error}", error=e)
            deployment_type = "localhost"  # Safe fallback

        health_report: FullHealthReport = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "unknown",
            "context_health": context_health,
            "session_state_health": session_health,
            "deployment_type": deployment_type,
            "recommendations": [],
        }

        # Determine overall health
        context_ok = context_health["context_available"]
        session_ok = session_health["test_passed"]
        fallback_used = context_health.get("fallback_used", False)

        recommendations = health_report["recommendations"]

        # FIX: Ubah logic health determination berdasarkan context dan session state
        if not context_ok and not session_ok:
            # Keduanya bermasalah = unhealthy
            health_report["overall_health"] = "unhealthy"
            recommendations.extend(
                [
                    "❌ Critical session functionality tidak tersedia",
                    "🔧 Restart aplikasi atau check Streamlit installation",
                    "📞 Contact developer jika masalah persists",
                ]
            )
        elif not context_ok and session_ok:
            # Context bermasalah, session OK = degraded
            health_report["overall_health"] = "degraded"
            recommendations.extend(
                [
                    "⚠️ Context features limited - using fallback values",
                    "💡 Consider checking Streamlit version compatibility",
                    "✅ Core functionality available - dapat melanjutkan operasi",
                ]
            )
        elif context_ok and session_ok:
            # Keduanya OK, cek fallback
            if fallback_used:
                health_report["overall_health"] = "healthy_with_fallbacks"
                recommendations.append(
                    "✅ System healthy - using fallback values untuk missing context"
                )
            else:
                health_report["overall_health"] = "healthy"
                recommendations.append("✅ System fully healthy - all features working")
        else:
            # Context OK tapi session bermasalah = unhealthy (session critical)
            health_report["overall_health"] = "unhealthy"
            recommendations.extend(
                [
                    "❌ Session state tidak tersedia",
                    "🔧 Restart aplikasi dan check session state",
                ]
            )

        # Deployment-specific recommendations
        if deployment_type == "lan":
            recommendations.append(
                "🌐 LAN deployment detected - optimal untuk MIM3 Dashboard"
            )
        elif deployment_type == "localhost":
            recommendations.append("🏠 Local development detected")

        logger.info(
            "Session health check complete",
            overall_health=health_report["overall_health"],
            deployment_type=deployment_type,
            fallback_used=fallback_used,
        )

        return health_report


# Convenience function untuk UI
def get_health_summary() -> str:
    """Get simple health summary untuk display."""
    try:
        health = SessionHealthCheck.run_full_health_check()
        status = health["overall_health"]

        status_messages = {
            "healthy": "🟢 Sistem Sehat",
            "healthy_with_fallbacks": "🟡 Sehat (Fallback Mode)",
            "degraded": "🟠 Terbatas (Masih Berfungsi)",
            "unhealthy": "🔴 Bermasalah",
        }

        return status_messages.get(status, "❓ Status Tidak Diketahui")

    except Exception as e:
        logger.error("Health check failed: {error}", error=e)
        return "🔴 Health Check Gagal"


# REMINDER: Production-ready health monitoring dengan fallback awareness
# TODO: Add Streamlit component untuk display health status di admin page
# PINNED: Fallback system memastikan aplikasi tetap berjalan walau context limited
