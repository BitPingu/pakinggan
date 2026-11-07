from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.user import User

# selects a recommended password-hashing config
password_hash = PasswordHash.recommended()

# extracts the bearer token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


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


# identifies the authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # validate and decode the token
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise credentials_exception

    # return the authenticated user
    return db_user
