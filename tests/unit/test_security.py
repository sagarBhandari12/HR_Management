from datetime import timedelta

import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)


@pytest.mark.unit
def test_password_hashing_and_verification():
    """Test Argon2 password hashing and verification."""
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


@pytest.mark.unit
def test_password_strength_validation():
    """Test password strength validation rules."""
    assert validate_password_strength("Short1!") is not None
    assert validate_password_strength("nouppercase123!") is not None
    assert validate_password_strength("NOLOWERCASE123!") is not None
    assert validate_password_strength("NoDigitsHere!") is not None
    assert validate_password_strength("NoSpecialChar123") is not None
    assert validate_password_strength("ValidPassword123!") is None


@pytest.mark.unit
def test_jwt_creation_and_decoding():
    """Test JWT access token creation and decoding."""
    token = create_access_token(subject="42", role="ADMIN")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload


@pytest.mark.unit
def test_expired_jwt_token_throws_unauthorized():
    """Test that expired JWT tokens raise UnauthorizedException."""
    token = create_access_token(
        subject="42", role="ADMIN", expires_delta=timedelta(seconds=-10)
    )
    with pytest.raises(UnauthorizedException):
        decode_access_token(token)
