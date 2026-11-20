import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.user import User

# Selects a recommended password-hashing configuration.
password_hash = PasswordHash.recommended()

# Extracts the bearer token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# Converts a plaintext password into a secure hash.
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Checks whether a submitted password matches the stored hash.
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# Generates a secure password-reset token and its SHA-256 hash.
def create_password_reset_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    return token, token_hash


# Calculates the expiration time for a password-reset token.
def get_password_reset_expiration() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=30)


# Hashes a submitted password-reset token for database comparison.
def hash_password_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# Creates a signed JWT containing the user's ID, token version, and expiration.
def create_access_token(subject: str, token_version: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "ver": token_version,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# Verifies the signature and expiration, then returns the token's payload.
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


# Identifies the authenticated user.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Validates and decodes the token.
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        token_version = payload.get("ver")

        if not isinstance(token_version, int) or isinstance(token_version, bool):
            raise credentials_exception

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None or db_user.token_version != token_version:
        raise credentials_exception

    # Returns the authenticated user.
    return db_user
