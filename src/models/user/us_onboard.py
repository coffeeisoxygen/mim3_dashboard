"""Account onboarding schemas - user registration & approval flow."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountRegister(BaseModel):
    """Model untuk user registrasi akun baru."""

    username: str = Field(min_length=3, max_length=50, description="Username unik")
    name: str = Field(min_length=2, max_length=50, description="Nama lengkap")
    password: str = Field(min_length=6, description="Password")
    role_id: int = Field(gt=0, description="Role yang diminta")
    model_config = ConfigDict(str_strip_whitespace=True)


class PendingAccount(BaseModel):
    """Model untuk display pending registrations."""

    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    role_name: str = Field(description="Role yang diminta")
    created_at: datetime = Field(description="Tanggal registrasi")
    model_config = ConfigDict(from_attributes=True)


class AccountApproval(BaseModel):
    """Model untuk admin approval action."""

    user_id: int = Field(gt=0, description="User ID yang akan di-approve")
    is_approved: bool = Field(description="Approve atau reject")
    notes: str | None = Field(None, max_length=200, description="Catatan admin")
    approved_by: int = Field(gt=0, description="Admin ID yang approve")
    model_config = ConfigDict(str_strip_whitespace=True)


class ApprovalResult(BaseModel):
    """Model untuk result dari approval operations."""

    success: bool = Field(description="Operasi berhasil atau tidak")
    message: str = Field(description="Pesan hasil operasi untuk UI")
