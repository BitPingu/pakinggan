from unittest.mock import AsyncMock, patch

import httpx
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
