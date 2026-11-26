import pytest

from app.core.encryption import encrypt_session_key
from app.models.lastfm_connection import LastFMConnection
from app.services import lastfm as lastfm_service
from app.services.lastfm import (
    get_user_lastfm_connection,
    get_user_now_playing,
    make_user_lastfm_request,
)


# Retrieves a user's Last.fm connection and decrypts its session key.
def test_get_user_lastfm_connection(db_session, user):
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="testuser",
        session_key=encrypt_session_key("test-session-key"),
    )

    db_session.add(connection)
    db_session.flush()

    result = get_user_lastfm_connection(user["id"], db_session)

    assert result is not None

    retrieved_connection, session_key = result

    assert retrieved_connection.lastfm_username == "testuser"
    assert session_key == "test-session-key"


# Returns None when the user has no Last.fm connection.
def test_get_user_lastfm_connection_not_found(db_session, user):
    result = get_user_lastfm_connection(user["id"], db_session)

    assert result is None


# Makes an authenticated Last.fm request using the user's stored session key.
@pytest.mark.asyncio
async def test_make_user_lastfm_request(db_session, user, monkeypatch):
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="testuser",
        session_key=encrypt_session_key("test-session-key"),
    )

    db_session.add(connection)
    db_session.flush()

    async def mock_authenticated_api_request(
        session_key,
        method,
        params=None,
    ):
        assert session_key == "test-session-key"
        assert method == "user.getRecentTracks"
        assert params == {"limit": "10"}

        return {"recenttracks": {"track": []}}

    monkeypatch.setattr(
        lastfm_service,
        "authenticated_api_request",
        mock_authenticated_api_request,
    )

    result = await make_user_lastfm_request(
        user_id=user["id"],
        method="user.getRecentTracks",
        db=db_session,
        params={"limit": "10"},
    )

    assert result == {"recenttracks": {"track": []}}


# Returns None when the user has no Last.fm connection.
@pytest.mark.asyncio
async def test_make_user_lastfm_request_not_connected(db_session, user):
    result = await make_user_lastfm_request(
        user_id=user["id"],
        method="user.getRecentTracks",
        db=db_session,
    )

    assert result is None


# Retrieves the user's currently playing track from Last.fm.
@pytest.mark.asyncio
async def test_get_user_now_playing(db_session, user, monkeypatch):
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="testuser",
        session_key=encrypt_session_key("test-session-key"),
    )

    db_session.add(connection)
    db_session.flush()

    expected_track = {
        "name": "Test Track",
        "artist": {"name": "Test Artist"},
        "@attr": {"nowplaying": "true"},
    }

    async def mock_get_now_playing(session_key, username):
        assert session_key == "test-session-key"
        assert username == "testuser"

        return expected_track

    monkeypatch.setattr(
        lastfm_service,
        "get_now_playing",
        mock_get_now_playing,
    )

    result = await get_user_now_playing(user["id"], db_session)

    assert result == expected_track


# Returns None when the user is not currently playing anything.
@pytest.mark.asyncio
async def test_get_user_now_playing_not_playing(db_session, user, monkeypatch):
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="testuser",
        session_key=encrypt_session_key("test-session-key"),
    )

    db_session.add(connection)
    db_session.flush()

    async def mock_get_now_playing(session_key, username):
        return None

    monkeypatch.setattr(
        lastfm_service,
        "get_now_playing",
        mock_get_now_playing,
    )

    result = await get_user_now_playing(user["id"], db_session)

    assert result is None


# Returns None when the user has no Last.fm connection.
@pytest.mark.asyncio
async def test_get_user_now_playing_not_connected(db_session, user, monkeypatch):
    async def mock_get_now_playing(session_key, username):
        pytest.fail("Last.fm should not be requested without a connection.")

    monkeypatch.setattr(
        lastfm_service,
        "get_now_playing",
        mock_get_now_playing,
    )

    result = await get_user_now_playing(user["id"], db_session)

    assert result is None
