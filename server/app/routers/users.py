import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import send_password_reset_email
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    get_current_user,
    get_password_reset_expiration,
    hash_password,
    hash_password_reset_token,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AccountDeletionRequest,
    ForgotPasswordRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

# Defines the API endpoints for user registration and authentication.
router = APIRouter(prefix="/api/users", tags=["Users"])

logger = logging.getLogger(__name__)


# Registers a new user account.
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )

    # Prevents registration with an existing username or email.
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    db_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=hash_password(user.password),
    )

    # Saves the new user to the database.
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# Authenticates a user and returns an access token.
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    # Verifies the submitted password against the stored hash.
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generates a JWT containing the user's database ID.
    access_token = create_access_token(
        subject=str(db_user.id),
        token_version=db_user.token_version,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# Sends a password-reset link without revealing whether an account exists.
@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    generic_response = {
        "message": (
            "If an account exists with that email, a password-reset link will be sent."
        )
    }

    db_user = db.query(User).filter(User.email == str(request.email)).first()

    # Returns the same response when no account matches the submitted email.
    if db_user is None:
        return generic_response

    # Generates a reset token and stores only its hash and expiration.
    token, token_hash = create_password_reset_token()
    db_user.password_reset_token_hash = token_hash
    db_user.password_reset_expires_at = get_password_reset_expiration()

    db.commit()

    # Builds the frontend URL containing the plaintext reset token.
    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"

    # Sends the reset email without exposing delivery failures to the requester.
    try:
        send_password_reset_email(db_user.email, reset_url)
    except Exception:
        logger.exception("Failed to send password-reset email")

    return generic_response


# Resets a user's password using a valid password-reset token.
@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    token_hash = hash_password_reset_token(request.token)

    db_user = (
        db.query(User).filter(User.password_reset_token_hash == token_hash).first()
    )

    # Rejects invalid or expired reset tokens.
    if db_user is None or db_user.password_reset_expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password-reset token",
        )

    expiration = db_user.password_reset_expires_at

    # Handles timestamps returned without timezone information by SQLite.
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)

    if expiration <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password-reset token",
        )

    # Updates the password and invalidates existing access tokens.
    db_user.hashed_password = hash_password(request.new_password)
    db_user.password_reset_token_hash = None
    db_user.password_reset_expires_at = None
    db_user.token_version += 1

    db.commit()

    return {"message": "Your password has been reset successfully."}


# Retrieves the authenticated user's profile.
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# Deletes the authenticated user's account after verifying their password.
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    request: AccountDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Requires the current password to confirm account ownership.
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Deletes the account without affecting the shared music library.
    db.delete(current_user)
    db.commit()


# Changes the authenticated user's password after verifying their current password.
@router.put("/me/password", response_model=PasswordResetResponse)
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verifies the current password before allowing the change.
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Prevents changing the password to its existing value.
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    # Updates the password and invalidates existing access tokens.
    current_user.hashed_password = hash_password(request.new_password)
    current_user.password_reset_token_hash = None
    current_user.password_reset_expires_at = None
    current_user.token_version += 1

    db.commit()

    return {"message": "Your password has been changed successfully."}
