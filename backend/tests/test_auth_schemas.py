"""Tests for auth schemas and security helpers."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import UserCreate


def test_hash_and_verify_password() -> None:
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip() -> None:
    token = create_access_token(subject="user-123")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"


def test_jwt_invalid() -> None:
    assert decode_access_token("not.a.token") is None


def test_user_create_password_min_length() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.com", password="short")
