import secrets

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.encryption import encrypt_session_key
from app.core.lastfm import get_auth_url, get_session
from app.core.security import (
    create_lastfm_state,
    decode_lastfm_state,
    get_current_user,
)
from app.database import get_db
from app.models.lastfm_connection import LastFMConnection
from app.models.user import User

# Defines the Last.fm API routes.
router = APIRouter(
    prefix="/api/lastfm",
    tags=["Last.fm"],
)


# Validates the Last.fm callback state against the browser cookie.
def validate_lastfm_state(state: str, request: Request) -> int:
    cookie_state = request.cookies.get("lastfm_state")

    if not cookie_state or not secrets.compare_digest(state, cookie_state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Last.fm authorization state.",
        )

    try:
        user_id = decode_lastfm_state(state)
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired Last.fm authorization state.",
        )

    return user_id


# Redirects the user and clears the Last.fm state cookie.
def redirect_lastfm(status_value: str) -> RedirectResponse:
    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/?lastfm={status_value}",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.delete_cookie(
        key="lastfm_state",
        path="/api/lastfm/callback",
    )

    return response


# Redirects the authenticated user to Last.fm authorization.
@router.get("/connect")
def connect_lastfm(current_user: User = Depends(get_current_user)):
    state = create_lastfm_state(current_user.id)

    callback_url = f"{settings.BACKEND_URL}/api/lastfm/callback?state={state}"

    auth_url = get_auth_url(callback_url)

    response = RedirectResponse(url=auth_url)

    # Stores the state token in a short-lived, HttpOnly cookie.
    response.set_cookie(
        key="lastfm_state",
        value=state,
        httponly=True,
        secure=settings.BACKEND_URL.startswith("https://"),
        samesite="lax",
        max_age=600,
        path="/api/lastfm/callback",
    )

    return response


# Handles the callback after Last.fm authorization.
@router.get("/callback")
async def callback_lastfm(
    request: Request,
    state: str,
    token: str | None = None,
    denied: str | None = None,
    db: Session = Depends(get_db),
):
    user_id = validate_lastfm_state(state, request)

    # Handles authorization declined by the user.
    if denied or not token:
        return redirect_lastfm("cancelled")

    # Exchanges the authorization token for a Last.fm session.
    try:
        lastfm_username, session_key = await get_session(token)
    except (httpx.HTTPError, ValueError):
        return redirect_lastfm("error")

    encrypted_session_key = encrypt_session_key(session_key)

    # Saves or updates the user's Last.fm connection.
    try:
        connection = (
            db.query(LastFMConnection)
            .filter(LastFMConnection.user_id == user_id)
            .first()
        )

        if connection:
            connection.lastfm_username = lastfm_username
            connection.session_key = encrypted_session_key
        else:
            connection = LastFMConnection(
                user_id=user_id,
                lastfm_username=lastfm_username,
                session_key=encrypted_session_key,
            )
            db.add(connection)

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return redirect_lastfm("error")

    # Redirects the user after successfully connecting Last.fm.
    return redirect_lastfm("connected")
