from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_lastfm_state,
    decode_access_token,
    decode_lastfm_state,
    get_current_user,
    hash_password,
    verify_password,
)


# Passwords are securely hashed using Argon2.
def test_hash_password():
    password = "test-password"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


# Correct passwords match their stored hashes.
def test_verify_password():
    password = "test-password"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


# Incorrect passwords do not match stored hashes.
def test_verify_incorrect_password():
    hashed_password = hash_password("test-password")

    assert not verify_password("wrong-password", hashed_password)


# Access tokens are generated as strings.
def test_create_access_token():
    token = create_access_token("1", 0)

    assert isinstance(token, str)


# Access tokens contain the user's ID, token version, and expiration.
def test_decode_access_token():
    token = create_access_token("1", 0)
    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["ver"] == 0
    assert "exp" in payload


# Expired access tokens cannot be decoded.
def test_decode_expired_access_token():
    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


# Invalid access tokens cannot be decoded.
def test_decode_invalid_access_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid-token")


# Valid access tokens identify the corresponding user.
def test_get_current_user_valid_token(db_session, user):
    token = create_access_token(str(user["id"]), 0)

    current_user = get_current_user(token, db_session)

    assert current_user.id == user["id"]
    assert current_user.username == user["username"]


# Invalid access tokens are rejected during authentication.
def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("invalid-token", db_session)

    assert exc_info.value.status_code == 401


# Expired access tokens are rejected during authentication.
def test_get_current_user_expired_token(db_session):
    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


# Access tokens referencing nonexistent users are rejected.
def test_get_current_user_nonexistent_user(db_session):
    token = create_access_token("9999", 0)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


# Last.fm authorization state tokens are generated as strings.
def test_create_lastfm_state():
    token = create_lastfm_state(1)

    assert isinstance(token, str)


# Last.fm authorization state tokens contain the user ID and purpose.
def test_decode_lastfm_state():
    token = create_lastfm_state(1)

    user_id = decode_lastfm_state(token)

    assert user_id == 1


# Expired Last.fm authorization state tokens cannot be decoded.
def test_decode_expired_lastfm_state():
    payload = {
        "sub": "1",
        "purpose": "lastfm",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_lastfm_state(token)


# Last.fm authorization state tokens with an invalid purpose are rejected.
def test_decode_invalid_lastfm_state_purpose():
    payload = {
        "sub": "1",
        "purpose": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_lastfm_state(token)


# Last.fm authorization state tokens with an invalid user ID are rejected.
@pytest.mark.parametrize("subject", ["invalid", "0", "-1", None])
def test_decode_invalid_lastfm_state_user_id(subject):
    payload = {
        "sub": subject,
        "purpose": "lastfm",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_lastfm_state(token)


# Invalid Last.fm authorization state tokens cannot be decoded.
def test_decode_invalid_lastfm_state_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_lastfm_state("invalid-token")
