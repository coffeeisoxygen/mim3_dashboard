"""class untuk mengelola halaman dinamis pada MIM3 Dashboard"""

import time
from dataclasses import dataclass
from enum import Enum

import streamlit as st
from loguru import logger


class PageCategory(Enum):
    """Kategori halaman untuk MIM3 Dashboard.

    Args:
        Enum (str): Nama kategori halaman.
    """

    DASHBOARD = "dashboard"
    REPORTS = "reports"
    ANALYTICS = "analytics"
    TOOLS = "tools"
    ADMIN = "admin"
    INFO = "info"
    ACCOUNT = "account"


@dataclass
class PageConfig:
    """Page configuration for dynamic page management"""

    file_path: str
    title: str
    icon: str
    category: PageCategory
    description: str = ""
    requires_auth: bool = True
    visible_for_roles: list[str] | None = None

    def __post_init__(self):
        """Menetapkan peran yang terlihat untuk halaman.

        Jika tidak ada peran yang ditentukan, halaman akan terlihat oleh semua peran.
        """
        if self.visible_for_roles is None:
            self.visible_for_roles = ["admin", "user", "viewer"]


class PageManager:
    """Centralized page management for MIM3 Dashboard"""

    def __init__(self):
        self.pages = self._register_pages()

    def _register_pages(self) -> dict[str, PageConfig]:
        """Register all pages with their configurations"""
        return {
            # Dashboard Pages
            "dashboard": PageConfig(
                file_path="ui/pages/dashboard/pg_dashboard.py",
                title="Dashboard",
                icon=":material/dashboard:",
                category=PageCategory.DASHBOARD,
                description="Main overview dashboard",
            ),
            # Report Pages - berdasarkan struktur Anda
            "allocation": PageConfig(
                file_path="ui/pages/reports/pg_allocation.py",
                title="Allocation Report",
                icon=":material/pie_chart:",
                category=PageCategory.REPORTS,
                description="Resource allocation analytics",
            ),
            "area": PageConfig(
                file_path="ui/pages/reports/pg_area.py",
                title="Area Analysis",
                icon=":material/map:",
                category=PageCategory.REPORTS,
                description="Regional performance analysis",
            ),
            "commission": PageConfig(
                file_path="ui/pages/reports/pg_commission.py",
                title="Commission Report",
                icon=":material/payments:",
                category=PageCategory.REPORTS,
                description="Commission calculations and tracking",
            ),
            "sales": PageConfig(
                file_path="ui/pages/reports/pg_sales.py",
                title="Sales Performance",
                icon=":material/trending_up:",
                category=PageCategory.REPORTS,
                description="Sales metrics and trends",
            ),
            "sellin": PageConfig(
                file_path="ui/pages/reports/pg_sellin.py",
                title="Sell-In Report",
                icon=":material/input:",
                category=PageCategory.REPORTS,
                description="Product sell-in analytics",
            ),
            "transaction": PageConfig(
                file_path="ui/pages/reports/pg_transaction.py",
                title="Transaction Analysis",
                icon=":material/receipt:",
                category=PageCategory.REPORTS,
                description="Transaction details and patterns",
            ),
            "transfer": PageConfig(
                file_path="ui/pages/reports/pg_transfer.py",
                title="Transfer Report",
                icon=":material/swap_horiz:",
                category=PageCategory.REPORTS,
                description="Transfer operations tracking",
            ),
            "reseller": PageConfig(
                file_path="ui/pages/reports/pg_reseller.py",  # Note: typo di nama file
                title="Reseller Analytics",
                icon=":material/store:",
                category=PageCategory.REPORTS,
                description="Reseller performance metrics",
            ),
            "site": PageConfig(
                file_path="ui/pages/reports/pg_site.py",
                title="Site Management",
                icon=":material/location_on:",
                category=PageCategory.REPORTS,
                description="Site operations and status",
            ),
            # Tools & Admin
            "upload": PageConfig(
                file_path="ui/pages/tools/pg_upload.py",
                title="Data Upload",
                icon=":material/upload:",
                category=PageCategory.TOOLS,
                description="Upload CSV and data files",
            ),
            "calculator": PageConfig(
                file_path="ui/pages/tools/pg_calculator.py",
                title="Calculator",
                icon=":material/calculate:",
                category=PageCategory.TOOLS,
                description="Simple calculator tool",
            ),
            "Ask AI": PageConfig(
                file_path="ui/pages/tools/pg_ask_ai.py",
                title="Ask AI",
                icon=":material/question_answer:",
                category=PageCategory.TOOLS,
                description="Interact with AI for insights",
            ),
            "glossarium": PageConfig(
                file_path="ui/pages/info/pg_glossarium.py",
                title="Glossarium",
                icon=":material/book:",
                category=PageCategory.INFO,
                description="Data Glossarium",
            ),
            "settings": PageConfig(
                file_path="ui/pages/admin/pg_glob_settings.py",
                title="Settings",
                icon=":material/settings:",
                category=PageCategory.ADMIN,
                description="System configuration",
                visible_for_roles=["admin"],
            ),
            "profile": PageConfig(
                file_path="ui/pages/account/pg_profile.py",
                title="Profile",
                icon=":material/person:",
                category=PageCategory.ACCOUNT,
                description="User profile management",
            ),
            "logout": PageConfig(
                file_path=None,  # Special case - handled by callback # type: ignore
                title="Logout",
                icon=":material/logout:",
                category=PageCategory.ACCOUNT,
                description="Logout from dashboard",
            ),
        }

    def get_pages_by_category(
        self, category: PageCategory, user_role: str = "user"
    ) -> dict[str, PageConfig]:
        """Get pages filtered by category and user role"""
        return {
            key: config
            for key, config in self.pages.items()
            if config.category == category
            and config.visible_for_roles is not None
            and user_role in config.visible_for_roles
        }

    def get_navigation_structure(
        self, user_role: str = "user"
    ) -> dict[str, list[st.Page]]:  # type: ignore
        """Build Streamlit navigation structure"""
        navigation = {}

        for category in PageCategory:
            pages = self.get_pages_by_category(category, user_role)

            if pages:
                # Convert to Streamlit Pages
                st_pages = []
                for key, config in pages.items():
                    try:
                        # ✅ Special handling for logout
                        if key == "logout":
                            page = st.Page(
                                self._logout_handler,  # Method callback
                                title=config.title,
                                icon=config.icon,
                            )
                        else:
                            # Regular page loading
                            page = st.Page(
                                config.file_path,
                                title=config.title,
                                icon=config.icon,
                                default=(key == "dashboard"),
                            )
                        st_pages.append(page)
                    except Exception as e:
                        st.error(f"Error loading page {config.title}: {e}")

                if st_pages:
                    navigation[category.value.title()] = st_pages

        return navigation

    def get_page_info(self, page_key: str) -> PageConfig | None:
        """Get page configuration by key"""
        return self.pages.get(page_key)

    @logger.catch
    def _logout_handler(self):
        """Handle logout page dengan confirmation."""
        st.title("🚪 Logout Confirmation")

        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        # User info
        st.info(f"👤 **{username}** ({role.title()})")
        st.write("Yakin ingin logout dari MIM3 Dashboard?")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("✅ Ya, Logout", type="primary", use_container_width=True):
                self._perform_logout()

            if st.button("❌ Batal", use_container_width=True):
                # Redirect ke dashboard
                st.switch_page("ui/pages/dashboard/pg_dashboard.py")

    def _perform_logout(self):
        """Perform actual logout operation."""
        try:
            from services.auth_service import AuthService

            auth_service = AuthService()
            success, message = auth_service.perform_logout()

            if success:
                st.success(f"✅ {message}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")

        except Exception as e:
            logger.error(f"Logout error: {e}")
            # Fallback: clear session state manually
            for key in ["logged_in", "username", "user_role", "session_token"]:
                if key in st.session_state:
                    del st.session_state[key]

            st.success("✅ Logged out successfully")
            time.sleep(1)
            st.rerun()
