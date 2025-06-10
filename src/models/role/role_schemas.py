"""Role CRUD operation schemas - only administrator can create, update, delete roles."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleCreate(BaseModel):
    """Model untuk admin create role baru."""

    name: str = Field(
        min_length=2,
        max_length=30,
        pattern="^[a-z_]+$",
        description="Nama role (lowercase, underscore allowed)",
    )
    description: str = Field(min_length=5, max_length=100, description="Deskripsi role")
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("name")
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """Validate role name tidak conflict dengan system roles."""
        system_roles = ["admin", "operator", "support"]
        if v in system_roles:
            raise ValueError(f"Role '{v}' adalah system role, tidak bisa dibuat ulang")
        return v.lower()


class RoleUpdate(BaseModel):
    """Model untuk admin update role yang sudah ada."""

    name: str | None = Field(
        None,
        min_length=2,
        max_length=30,
        pattern="^[a-z_]+$",
        description="Nama role baru",
    )
    description: str | None = Field(
        None, min_length=5, max_length=100, description="Deskripsi role baru"
    )
    model_config = ConfigDict(str_strip_whitespace=True)


class RoleView(BaseModel):
    """Model untuk display role data ke admin."""

    id: int = Field(description="Role ID")
    name: str = Field(description="Nama role")
    description: str = Field(description="Deskripsi role")
    is_active: bool = Field(description="Status aktif role")
    user_count: int = Field(ge=0, description="Jumlah user dengan role ini")
    created_at: datetime = Field(description="Tanggal dibuat")
    model_config = ConfigDict(from_attributes=True)


class RoleActionResult(BaseModel):
    """Model untuk result dari role operations."""

    success: bool = Field(description="Operasi berhasil atau tidak")
    affected_users: int = Field(ge=0, description="Jumlah user yang terpengaruh")
    message: str = Field(description="Pesan hasil operasi")


class RoleOption(BaseModel):
    """Model untuk role dropdown di registration form."""

    id: int = Field(gt=0, description="Role ID")
    name: str = Field(description="Nama role")
    description: str = Field(description="Deskripsi role")

    model_config = ConfigDict(from_attributes=True)


class UserRegistration(BaseModel):
    """Model untuk user self-registration."""

    username: str = Field(min_length=3, max_length=50, description="Username unik")
    name: str = Field(min_length=2, max_length=100, description="Nama lengkap")
    password: str = Field(min_length=6, description="Password")
    requested_role_id: int = Field(
        default=2,  # Default "operator" role
        gt=0,
        description="Role yang diminta",
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class RegistrationResult(BaseModel):
    """Result untuk registration operation."""

    success: bool = Field(description="Registration berhasil atau tidak")
    user_id: int | None = Field(default=None, description="User ID yang dibuat")
    message: str = Field(description="Pesan hasil registration")
    requires_approval: bool = Field(default=True, description="Butuh approval admin")


class SystemRoleCreate(BaseModel):
    """Model khusus untuk system role seeding - no validation."""

    name: str = Field(description="System role name")
    description: str = Field(description="System role description")
    model_config = ConfigDict(str_strip_whitespace=True)
