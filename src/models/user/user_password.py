"""Unified password module - generation, validation, utilities."""

from __future__ import annotations

import re
import secrets
import string
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ================================
# Password Configuration
# ================================


@dataclass(frozen=True)
class PasswordPolicy:
    """Centralized password policy configuration."""

    min_length: int = 6
    max_length: int = 20
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    allow_spaces: bool = False
    special_chars: str = '!@#$%^&*(),.?":{}|<>'

    # Generation settings
    exclude_ambiguous: bool = True  # Remove l, I, O, 0, 1
    generation_symbols: str = "!@#$%^&*"  # Simpler for generation


# Global policy instance
PASSWORD_POLICY = PasswordPolicy()


# ================================
# Password Validation
# ================================


def validate_password_strength(password: str) -> str:
    """Validate password strength - centralized policy.

    Uses global PASSWORD_POLICY configuration.
    """
    policy = PASSWORD_POLICY

    if len(password) < policy.min_length or len(password) > policy.max_length:
        raise ValueError(
            f"Password harus {policy.min_length}-{policy.max_length} karakter"
        )

    if not policy.allow_spaces and " " in password:
        raise ValueError("Password tidak boleh mengandung spasi")

    if policy.require_uppercase and not re.search(r"[A-Z]", password):
        raise ValueError("Password harus mengandung minimal 1 huruf besar")

    if policy.require_lowercase and not re.search(r"[a-z]", password):
        raise ValueError("Password harus mengandung minimal 1 huruf kecil")

    if policy.require_digit and not re.search(r"\d", password):
        raise ValueError("Password harus mengandung minimal 1 angka")

    if policy.require_special and not re.search(
        f"[{re.escape(policy.special_chars)}]", password
    ):
        raise ValueError(
            f"Password harus mengandung minimal 1 karakter khusus ({policy.special_chars})"
        )

    return password


def validate_password_match(new_password: str, confirm_password: str) -> bool:
    """Validate password confirmation matches."""
    if new_password != confirm_password:
        raise ValueError("Password baru dan konfirmasi tidak cocok")
    return True


def validate_password_change(current_password: str, new_password: str) -> bool:
    """Validate password change rules."""
    if current_password == new_password:
        raise ValueError("Password baru harus berbeda dari password lama")
    return True


# ================================
# Password Generation
# ================================


def generate_secure_password(length: int = 8) -> str:
    """Generate secure password with policy compliance.

    Uses global PASSWORD_POLICY for configuration.
    """
    policy = PASSWORD_POLICY

    if length < policy.min_length or length > policy.max_length:
        raise ValueError(
            f"Password length must be {policy.min_length}-{policy.max_length} characters"
        )

    # Character sets
    if policy.exclude_ambiguous:
        # Remove ambiguous chars for better UX
        letters = (
            string.ascii_letters.replace("l", "").replace("I", "").replace("O", "")
        )
        numbers = string.digits.replace("0", "").replace("1", "")
    else:
        letters = string.ascii_letters
        numbers = string.digits

    symbols = policy.generation_symbols

    # Ensure policy compliance
    password_chars = []

    if policy.require_uppercase:
        password_chars.append(secrets.choice([c for c in letters if c.isupper()]))
    if policy.require_lowercase:
        password_chars.append(secrets.choice([c for c in letters if c.islower()]))
    if policy.require_digit:
        password_chars.append(secrets.choice(numbers))
    if policy.require_special:
        password_chars.append(secrets.choice(symbols))

    # Fill remaining length
    all_chars = letters + numbers + symbols
    password_chars.extend(
        secrets.choice(all_chars) for _ in range(length - len(password_chars))
    )

    # Shuffle untuk random positioning
    secrets.SystemRandom().shuffle(password_chars)

    generated = "".join(password_chars)

    # Validate generated password meets policy (safety check)
    validate_password_strength(generated)

    return generated


# ================================
# Password Pydantic Models
# ================================


class PasswordField(BaseModel):
    """Reusable password field dengan validation."""

    password: str = Field(min_length=6, max_length=20, description="Password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        return validate_password_strength(v)


class PasswordChangeModel(BaseModel):
    """Model untuk password change dengan confirmation."""

    current_password: str = Field(min_length=6, max_length=20)
    new_password: str = Field(min_length=6, max_length=20)
    confirm_password: str = Field(min_length=6, max_length=20)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        return validate_password_strength(v)

    @model_validator(mode="after")
    def validate_password_rules(self):
        """Validate password confirmation and change rules."""
        # Check confirmation match
        if self.new_password != self.confirm_password:
            raise ValueError("Password baru dan konfirmasi tidak cocok")

        # Check different from current
        if self.current_password == self.new_password:
            raise ValueError("Password baru harus berbeda dari password lama")

        return self


class PasswordGenerationOptions(BaseModel):
    """Options untuk password generation."""

    length: int = Field(default=8, ge=6, le=20, description="Password length")
    exclude_ambiguous: bool = Field(default=True, description="Exclude l,I,O,0,1")
    custom_symbols: str = Field(default="@", description="Custom symbol set")

    def generate(self) -> str:
        """Generate password dengan options ini."""
        return generate_secure_password(self.length)


# ================================
# Utility Functions
# ================================


def estimate_password_strength(password: str) -> dict[str, Any]:
    """Estimate password strength untuk UI feedback."""
    score = 0
    feedback = []

    # Length score
    if len(password) >= 12:
        score += 25
        feedback.append("✅ Panjang password baik")
    elif len(password) >= 8:
        score += 15
        feedback.append("🟡 Panjang password cukup")
    else:
        feedback.append("❌ Password terlalu pendek")

    # Character variety
    if re.search(r"[A-Z]", password):
        score += 20
        feedback.append("✅ Mengandung huruf besar")
    else:
        feedback.append("❌ Perlu huruf besar")

    if re.search(r"[a-z]", password):
        score += 20

    if re.search(r"\d", password):
        score += 20
        feedback.append("✅ Mengandung angka")
    else:
        feedback.append("❌ Perlu angka")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 15
        feedback.append("✅ Mengandung simbol")
    else:
        feedback.append("❌ Perlu simbol")

    # Strength level
    if score >= 80:
        level = "Very Strong"
        color = "green"
    elif score >= 60:
        level = "Strong"
        color = "lightgreen"
    elif score >= 40:
        level = "Medium"
        color = "orange"
    else:
        level = "Weak"
        color = "red"

    return {"score": score, "level": level, "color": color, "feedback": feedback}


# REMINDER: Single import untuk semua password functionality
# TODO: Add password history validation (don't reuse last N passwords)
# PINNED: All password logic centralized - easy to maintain and test
