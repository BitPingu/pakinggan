from sqlalchemy.orm import Session

from app.core.encryption import decrypt_session_key
from app.core.lastfm import authenticated_api_request, get_now_playing
from app.models.lastfm_connection import LastFMConnection


# Retrieves the user's Last.fm connection and decrypts its session key.
def get_user_lastfm_connection(
    user_id: int,
    db: Session,
) -> tuple[LastFMConnection, str] | None:
    connection = (
        db.query(LastFMConnection).filter(LastFMConnection.user_id == user_id).first()
    )

    if not connection:
        return None

    session_key = decrypt_session_key(connection.session_key)

    return connection, session_key


# Makes an authenticated Last.fm API request for the user.
async def make_user_lastfm_request(
    user_id: int,
    method: str,
    db: Session,
    params: dict[str, str] | None = None,
) -> dict | None:
    connection_data = get_user_lastfm_connection(user_id, db)

    if not connection_data:
        return None

    _, session_key = connection_data

    return await authenticated_api_request(
        session_key=session_key,
        method=method,
        params=params,
    )


# Retrieves the user's currently playing track from Last.fm.
async def get_user_now_playing(
    user_id: int,
    db: Session,
) -> dict | None:
    connection_data = get_user_lastfm_connection(user_id, db)

    if not connection_data:
        return None

    connection, session_key = connection_data

    return await get_now_playing(
        session_key=session_key,
        username=connection.lastfm_username,
    )
