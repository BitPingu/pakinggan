import json
import secrets

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response
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
from app.schemas.lastfm import (
    LastFMNowPlaying,
    LastFMRecentTracks,
    LastFMStatus,
)
from app.services.lastfm import make_user_lastfm_request

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
        url=f"{settings.FRONTEND_URL}/settings?lastfm={status_value}",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.delete_cookie(
        key="lastfm_state",
        path="/api/lastfm/callback",
    )

    return response


# Returns the Last.fm authorization URL for the authenticated user.
@router.get("/connect")
def connect_lastfm(current_user: User = Depends(get_current_user)):
    state = create_lastfm_state(current_user.id)

    callback_url = f"{settings.BACKEND_URL}/api/lastfm/callback?state={state}"

    auth_url = get_auth_url(callback_url)

    # Returns the authorization URL and stores the state in a secure cookie.
    response = Response(
        content=json.dumps({"auth_url": auth_url}),
        media_type="application/json",
    )

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


# Returns the authenticated user's Last.fm connection status.
@router.get("/status", response_model=LastFMStatus)
def get_lastfm_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    connection = (
        db.query(LastFMConnection)
        .filter(LastFMConnection.user_id == current_user.id)
        .first()
    )

    return LastFMStatus(
        connected=connection is not None,
        lastfm_username=(connection.lastfm_username if connection else None),
    )


# Returns the authenticated user's recently played Last.fm tracks.
@router.get("/recent-tracks", response_model=LastFMRecentTracks)
async def get_recent_tracks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Requests recent tracks from the connected Last.fm account.
    try:
        data = await make_user_lastfm_request(
            user_id=current_user.id,
            method="user.getRecentTracks",
            db=db,
            params={"limit": "20", "extended": "1"},
        )
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve recent tracks from Last.fm.",
        ) from exc

    # Requires the user to connect a Last.fm account.
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Last.fm account is not connected.",
        )

    # Extracts and validates the recent tracks from the Last.fm response.
    recent_tracks_data = data.get("recenttracks")

    if not isinstance(recent_tracks_data, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Last.fm.",
        )

    recent_tracks = recent_tracks_data.get("track", [])

    if not isinstance(recent_tracks, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Last.fm.",
        )

    # Validates each track in the Last.fm response.
    if not all(isinstance(track, dict) for track in recent_tracks):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Last.fm.",
        )

    # Validates the nested track data used by the application.
    for track in recent_tracks:
        if not isinstance(track.get("artist"), dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from Last.fm.",
            )

        for field in ("album", "date"):
            value = track.get(field)

            if value is not None and not isinstance(value, dict):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid response from Last.fm.",
                )

        # Validates the track image data.
        images = track.get("image", [])

        if not isinstance(images, list) or not all(
            isinstance(image, dict) for image in images
        ):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from Last.fm.",
            )

    # Converts the Last.fm response into the application response schema.
    tracks = [
        {
            "name": track.get("name", ""),
            "artist": track.get("artist", {}).get("#text", ""),
            "album": (track.get("album") or {}).get("#text"),
            "url": track.get("url"),
            "image": (track["image"][-1].get("#text") if track.get("image") else None),
            "played_at": (track.get("date") or {}).get("#text"),
            "uts": (track.get("date") or {}).get("uts"),
        }
        for track in recent_tracks
    ]

    return LastFMRecentTracks(tracks=tracks)


# Returns the authenticated user's currently playing Last.fm track.
@router.get("/now-playing", response_model=LastFMNowPlaying)
async def get_now_playing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Requests the most recent track from the connected Last.fm account.
    try:
        data = await make_user_lastfm_request(
            user_id=current_user.id,
            method="user.getRecentTracks",
            db=db,
            params={"limit": "1", "extended": "1"},
        )
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve currently playing track from Last.fm.",
        ) from exc

    # Requires the user to connect a Last.fm account.
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Last.fm account is not connected.",
        )

    # Extracts the most recent track from the Last.fm response.
    recent_tracks_data = data.get("recenttracks")

    if not isinstance(recent_tracks_data, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Last.fm.",
        )

    recent_tracks = recent_tracks_data.get("track", [])

    if not isinstance(recent_tracks, list) or not all(
        isinstance(track, dict) for track in recent_tracks
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Last.fm.",
        )

    # Finds the currently playing track.
    for track in recent_tracks:
        attributes = track.get("@attr", {})

        if not isinstance(attributes, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from Last.fm.",
            )

        if attributes.get("nowplaying") == "true":
            artist = track.get("artist")
            album = track.get("album")
            images = track.get("image", [])

            if (
                not isinstance(artist, dict)
                or (album is not None and not isinstance(album, dict))
                or not isinstance(images, list)
                or not all(isinstance(image, dict) for image in images)
            ):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid response from Last.fm.",
                )

            return LastFMNowPlaying(
                track={
                    "name": track.get("name", ""),
                    "artist": artist.get("#text", ""),
                    "album": (album or {}).get("#text"),
                    "url": track.get("url"),
                    "image": images[-1].get("#text") if images else None,
                    "nowplaying": True,
                }
            )

    # Returns an empty result when no track is currently playing.
    return LastFMNowPlaying(track=None)


# Disconnects the authenticated user's Last.fm account.
@router.delete("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_lastfm(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    connection = (
        db.query(LastFMConnection)
        .filter(LastFMConnection.user_id == current_user.id)
        .first()
    )

    # Deletes the user's Last.fm connection if one exists.
    if connection:
        db.delete(connection)
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
