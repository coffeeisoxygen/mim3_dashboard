"""Common utilities untuk User domain - reusable components only."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OperationResult(BaseModel):
    """Standard operation result pattern."""

    success: bool = Field(description="Operation berhasil atau tidak")
    message: str | None = Field(default=None, description="Pesan hasil operation")


class TimestampFields(BaseModel):
    """Reusable timestamp fields untuk database models."""

    created_at: datetime = Field(description="Waktu pembuatan")
    updated_at: datetime | None = Field(
        default=None, description="Waktu update terakhir"
    )
