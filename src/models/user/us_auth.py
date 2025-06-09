"""Authentication schemas untuk user."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type UserRole = Literal["admin", "operator", "team_indosat"]

ROLE_ID_MAPPING: dict[int, UserRole] = {
    1: "admin",
    2: "operator",
    3: "team_indosat",
}


class UserLogin(BaseModel):
    """Model untuk login request."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserSession(BaseModel):
    """Model untuk user session data."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap user")
    role: UserRole = Field(description="User role")
    login_time: datetime = Field(default_factory=datetime.now)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_data(cls, user_data: dict) -> UserSession:
        """Create UserSession dari database data."""
        role_id = user_data["role_id"]
        role = ROLE_ID_MAPPING.get(role_id, "operator")  # fallback default

        return cls(
            user_id=user_data["id"],
            username=user_data["username"],
            name=user_data["name"],
            role=role,
        )


class AuthResult(BaseModel):
    """Model untuk authentication result."""

    success: bool = Field(description="Authentication berhasil atau tidak")
    user_session: UserSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
    error_message: str | None = Field(
        default=None, description="Error message jika gagal"
    )
