from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app.core.config import settings
from app.core.lastfm import generate_api_signature, get_auth_url, get_session


# Tests that API signatures are generated correctly.
def test_generate_api_signature(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    params = {
        "method": "auth.getSession",
        "api_key": "test_api_key",
        "token": "test_token",
    }

    signature = generate_api_signature(params)

    assert signature == "1f048ad9be7323c038c9dc4b46a9ee79"


# Tests that parameter order does not affect the generated signature.
def test_generate_api_signature_is_order_independent(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    first_params = {
        "method": "auth.getSession",
        "api_key": "test_api_key",
        "token": "test_token",
    }

    second_params = {
        "token": "test_token",
        "api_key": "test_api_key",
        "method": "auth.getSession",
    }

    assert generate_api_signature(first_params) == generate_api_signature(second_params)


# Tests that the authorization URL is generated correctly.
def test_get_auth_url(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    callback_url = "http://localhost:5173/settings/integrations"

    url = get_auth_url(callback_url)
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == "www.last.fm"
    assert parsed_url.path == "/api/auth/"
    assert params["api_key"] == ["test_api_key"]
    assert params["cb"] == [callback_url]


# Tests that callback URLs containing query parameters are encoded correctly.
def test_get_auth_url_encodes_callback_url(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    callback_url = "http://localhost:5173/callback?source=lastfm&test=true"

    url = get_auth_url(callback_url)
    params = parse_qs(urlparse(url).query)

    assert params["cb"] == [callback_url]


# Tests that a session key is returned after successful authentication.
@pytest.mark.asyncio
async def test_get_session(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "auth.getSession"
        assert params["api_key"] == "test_api_key"
        assert params["token"] == "test_token"
        assert "api_sig" in params
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "session": {
                    "name": "test_user",
                    "key": "test_session_key",
                    "subscriber": 0,
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        lastfm_username, session_key = await get_session("test_token", client)

    assert lastfm_username == "test_user"
    assert session_key == "test_session_key"


# Tests that Last.fm API errors are handled correctly.
@pytest.mark.asyncio
async def test_get_session_api_error(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(
            200,
            json={
                "error": 4,
                "message": "Invalid authentication token.",
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(
            ValueError,
            match="Invalid authentication token.",
        ):
            await get_session("invalid_token", client)


# Tests that HTTP errors are raised when a request fails.
@pytest.mark.asyncio
async def test_get_session_http_error(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(
            500,
            json={"message": "Internal Server Error"},
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await get_session("test_token", client)


# Tests that network connection errors are raised correctly.
@pytest.mark.asyncio
async def test_get_session_connection_error(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        raise httpx.ConnectError("Connection failed")

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.ConnectError, match="Connection failed"):
            await get_session("test_token", client)


# Tests that missing session data raises an error.
@pytest.mark.asyncio
async def test_get_session_missing_session(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid Last.fm session response."):
            await get_session("test_token", client)


# Tests that a missing session key raises an error.
@pytest.mark.asyncio
async def test_get_session_missing_key(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(
            200,
            json={
                "session": {
                    "name": "test_user",
                    "subscriber": 0,
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid Last.fm session key."):
            await get_session("test_token", client)


# Tests that a missing Last.fm username raises an error.
@pytest.mark.asyncio
async def test_get_session_missing_username(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(
            200,
            json={
                "session": {
                    "key": "test_session_key",
                    "subscriber": 0,
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid Last.fm username."):
            await get_session("test_token", client)


# Tests that an invalid API response raises an error.
@pytest.mark.asyncio
async def test_get_session_invalid_response(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")
    monkeypatch.setattr(settings, "LASTFM_SHARED_SECRET", "test_secret")

    async def mock_handler(request):
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid Last.fm API response."):
            await get_session("test_token", client)
