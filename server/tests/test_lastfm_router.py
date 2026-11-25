from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import create_lastfm_state
from app.models.lastfm_connection import LastFMConnection


# Authenticated users are redirected to Last.fm with a state cookie.
def test_connect_lastfm(client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    # Mocks the Last.fm authorization URL.
    with patch(
        "app.routers.lastfm.get_auth_url",
        return_value="https://www.last.fm/api/auth/?mocked",
    ) as mock_auth_url:
        response = client.get(
            "/api/lastfm/connect",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
        )

    assert response.status_code == 307
    assert response.headers["location"] == ("https://www.last.fm/api/auth/?mocked")

    # Verifies that the callback URL contains the authorization state.
    callback_url = mock_auth_url.call_args.args[0]

    assert callback_url.startswith("http://localhost:8000/api/lastfm/callback?state=")

    # Verifies that the state cookie is configured securely.
    state_cookie = response.cookies.get("lastfm_state")

    assert state_cookie is not None
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "max-age=600" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()
    assert "path=/api/lastfm/callback" in response.headers["set-cookie"].lower()


# Unauthenticated users cannot connect a Last.fm account.
def test_connect_lastfm_unauthenticated(client):
    response = client.get(
        "/api/lastfm/connect",
        follow_redirects=False,
    )

    assert response.status_code == 401


# Callback requests with a missing state cookie are rejected.
def test_callback_lastfm_missing_state_cookie(client, user):
    state = create_lastfm_state(user["id"])

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Last.fm authorization state."


# Callback requests with mismatched state values are rejected.
def test_callback_lastfm_invalid_state(client, user):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        "different-state",
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Last.fm authorization state."


# Callback requests with an invalid state token are rejected.
def test_callback_lastfm_invalid_token(client):
    invalid_state = "invalid-token"

    client.cookies.set(
        "lastfm_state",
        invalid_state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": invalid_state, "token": "mock-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid or expired Last.fm authorization state."
    )


# Authorization declined by the user redirects to the frontend.
def test_callback_lastfm_authorization_cancelled(client, user):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "denied": "1"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=cancelled")
    assert "lastfm_state" in response.headers["set-cookie"]


# Missing authorization tokens are treated as cancelled requests.
def test_callback_lastfm_missing_token(client, user):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=cancelled")


# Last.fm API failures redirect the user to the frontend with an error.
@patch(
    "app.routers.lastfm.get_session",
    new_callable=AsyncMock,
    side_effect=ValueError("Last.fm API request failed."),
)
def test_callback_lastfm_api_error(mock_get_session, client, user):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=error")

    mock_get_session.assert_awaited_once_with("mock-token")


# A successful callback creates a new Last.fm connection.
@patch(
    "app.routers.lastfm.encrypt_session_key",
    return_value="encrypted-session-key",
)
@patch(
    "app.routers.lastfm.get_session",
    new_callable=AsyncMock,
    return_value=("radiohead_fan", "mock-session-key"),
)
def test_callback_lastfm_create_connection(
    mock_get_session,
    mock_encrypt,
    client,
    user,
    db_session,
):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=connected")

    # Verifies that the Last.fm connection was saved.
    connection = (
        db_session.query(LastFMConnection)
        .filter(LastFMConnection.user_id == user["id"])
        .first()
    )

    assert connection is not None
    assert connection.lastfm_username == "radiohead_fan"
    assert connection.session_key == "encrypted-session-key"

    mock_get_session.assert_awaited_once_with("mock-token")
    mock_encrypt.assert_called_once_with("mock-session-key")


# A successful callback updates an existing Last.fm connection.
@patch(
    "app.routers.lastfm.encrypt_session_key",
    return_value="new-encrypted-session-key",
)
@patch(
    "app.routers.lastfm.get_session",
    new_callable=AsyncMock,
    return_value=("new_username", "new-session-key"),
)
def test_callback_lastfm_update_connection(
    mock_get_session,
    mock_encrypt,
    client,
    user,
    db_session,
):
    # Creates an existing Last.fm connection.
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="old_username",
        session_key="old-encrypted-session-key",
    )

    db_session.add(connection)
    db_session.commit()

    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=connected")

    # Verifies that the existing connection was updated.
    db_session.refresh(connection)

    assert connection.lastfm_username == "new_username"
    assert connection.session_key == "new-encrypted-session-key"

    mock_get_session.assert_awaited_once_with("mock-token")
    mock_encrypt.assert_called_once_with("new-session-key")


# Database failures roll back the transaction and redirect with an error.
@patch(
    "app.routers.lastfm.encrypt_session_key",
    return_value="encrypted-session-key",
)
@patch(
    "app.routers.lastfm.get_session",
    new_callable=AsyncMock,
    return_value=("radiohead_fan", "mock-session-key"),
)
def test_callback_lastfm_database_error(
    mock_get_session,
    mock_encrypt,
    client,
    user,
    db_session,
):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    with patch.object(
        db_session,
        "commit",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.get(
            "/api/lastfm/callback",
            params={"state": state, "token": "mock-token"},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=error")

    mock_get_session.assert_awaited_once_with("mock-token")
    mock_encrypt.assert_called_once_with("mock-session-key")


# Network failures redirect the user to the frontend with an error.
@patch(
    "app.routers.lastfm.get_session",
    new_callable=AsyncMock,
    side_effect=httpx.ConnectError("Connection failed."),
)
def test_callback_lastfm_connection_error(mock_get_session, client, user):
    state = create_lastfm_state(user["id"])

    client.cookies.set(
        "lastfm_state",
        state,
        path="/api/lastfm/callback",
    )

    response = client.get(
        "/api/lastfm/callback",
        params={"state": state, "token": "mock-token"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/?lastfm=error")

    mock_get_session.assert_awaited_once_with("mock-token")


# Authenticated users without a Last.fm connection receive a disconnected status.
def test_get_lastfm_status_disconnected(client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "connected": False,
        "lastfm_username": None,
    }


# Authenticated users with a Last.fm connection receive a connected status.
def test_get_lastfm_status_connected(client, user, db_session):
    # Creates an existing Last.fm connection.
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="radiohead_fan",
        session_key="encrypted-session-key",
    )

    db_session.add(connection)
    db_session.commit()

    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "connected": True,
        "lastfm_username": "radiohead_fan",
    }


# Unauthenticated users cannot retrieve their Last.fm connection status.
def test_get_lastfm_status_unauthenticated(client):
    response = client.get("/api/lastfm/status")

    assert response.status_code == 401


# Authenticated users can disconnect their Last.fm account.
def test_disconnect_lastfm(client, user, db_session):
    # Creates an existing Last.fm connection.
    connection = LastFMConnection(
        user_id=user["id"],
        lastfm_username="radiohead_fan",
        session_key="encrypted-session-key",
    )

    db_session.add(connection)
    db_session.commit()

    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.delete(
        "/api/lastfm/disconnect",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.content == b""

    # Verifies the Last.fm connection was deleted.
    assert (
        db_session.query(LastFMConnection)
        .filter(LastFMConnection.user_id == user["id"])
        .first()
        is None
    )


# Users can disconnect even when no Last.fm connection exists.
def test_disconnect_lastfm_already_disconnected(client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.delete(
        "/api/lastfm/disconnect",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.content == b""


# Unauthenticated users cannot disconnect a Last.fm account.
def test_disconnect_lastfm_unauthenticated(client):
    response = client.delete("/api/lastfm/disconnect")

    assert response.status_code == 401


# Authenticated users can retrieve their recently played Last.fm tracks.
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
)
def test_get_recent_tracks(mock_lastfm_request, client, user):
    mock_lastfm_request.return_value = {
        "recenttracks": {
            "track": [
                {
                    "name": "Paranoid Android",
                    "artist": {"#text": "Radiohead"},
                    "album": {"#text": "OK Computer"},
                    "url": "https://www.last.fm/music/Radiohead/_/Paranoid+Android",
                    "image": [
                        {"#text": "small-image-url"},
                        {"#text": "large-image-url"},
                    ],
                    "date": {"#text": "22 Nov 2026, 12:00"},
                }
            ]
        }
    }

    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tracks": [
            {
                "name": "Paranoid Android",
                "artist": "Radiohead",
                "album": "OK Computer",
                "url": "https://www.last.fm/music/Radiohead/_/Paranoid+Android",
                "image": "large-image-url",
                "played_at": "22 Nov 2026, 12:00",
                "nowplaying": False,
            }
        ]
    }

    mock_lastfm_request.assert_awaited_once_with(
        user_id=user["id"],
        method="user.getRecentTracks",
        db=mock_lastfm_request.call_args.kwargs["db"],
        params={"limit": "20", "extended": "1"},
    )


# Users without a Last.fm connection cannot retrieve recent tracks.
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
    return_value=None,
)
def test_get_recent_tracks_not_connected(mock_lastfm_request, client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Last.fm account is not connected."

    mock_lastfm_request.assert_awaited_once()


# Last.fm API errors return a bad gateway response.
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
    side_effect=ValueError("Last.fm API request failed."),
)
def test_get_recent_tracks_api_error(mock_lastfm_request, client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to retrieve recent tracks from Last.fm."
    )

    mock_lastfm_request.assert_awaited_once()


# Network failures return a bad gateway response.
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
    side_effect=httpx.ConnectError("Connection failed."),
)
def test_get_recent_tracks_connection_error(
    mock_lastfm_request,
    client,
    user,
):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to retrieve recent tracks from Last.fm."
    )

    mock_lastfm_request.assert_awaited_once()


# Invalid Last.fm response structures return a bad gateway response.
@pytest.mark.parametrize(
    "api_response",
    [
        {},
        {"recenttracks": []},
        {"recenttracks": {"track": {}}},
        {"recenttracks": {"track": ["invalid-track"]}},
        {"recenttracks": {"track": [{"artist": "Radiohead"}]}},
        {"recenttracks": {"track": [{"artist": {}, "image": "invalid-image"}]}},
    ],
)
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
)
def test_get_recent_tracks_invalid_response(
    mock_lastfm_request,
    client,
    user,
    api_response,
):
    mock_lastfm_request.return_value = api_response

    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Invalid response from Last.fm."

    mock_lastfm_request.assert_awaited_once()


# Users with no recent tracks receive an empty track list.
@patch(
    "app.routers.lastfm.make_user_lastfm_request",
    new_callable=AsyncMock,
    return_value={"recenttracks": {"track": []}},
)
def test_get_recent_tracks_empty(mock_lastfm_request, client, user):
    # Logs in to obtain an access token.
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/lastfm/recent-tracks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"tracks": []}

    mock_lastfm_request.assert_awaited_once()


# Unauthenticated users cannot retrieve recent tracks.
def test_get_recent_tracks_unauthenticated(client):
    response = client.get("/api/lastfm/recent-tracks")

    assert response.status_code == 401
