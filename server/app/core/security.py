from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# selects a recommended password-hashing config
password_hash = PasswordHash.recommended()


# converts a plaintext password into a secure hash
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# checks whether a submitted password matches the stored hash
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# creates a signed JWT containing the user's identifier and expiration time
def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,  # user's identifier
        "exp": expires_at,  # expiration time
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# verifies the signature and expiration, then returns the token's payload
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
