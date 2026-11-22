import hashlib
from urllib.parse import urlencode

import httpx

from app.core.config import settings


# Generates an API signature for authenticated Last.fm requests.
def generate_api_signature(params: dict[str, str]) -> str:
    signature_base = "".join(f"{key}{value}" for key, value in sorted(params.items()))

    signature_base += settings.LASTFM_SHARED_SECRET

    return hashlib.md5(signature_base.encode("utf-8")).hexdigest()


# Generates a Last.fm authorization URL.
def get_auth_url(callback_url: str) -> str:
    params = {
        "api_key": settings.LASTFM_API_KEY,
        "cb": callback_url,
    }

    return f"https://www.last.fm/api/auth/?{urlencode(params)}"


# Sends a request to the Last.fm API.
async def make_api_request(
    params: dict[str, str],
    client: httpx.AsyncClient | None = None,
) -> dict:
    # Sends the request using the provided or a temporary HTTP client.
    if client is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://ws.audioscrobbler.com/2.0/",
                params=params,
            )
    else:
        response = await client.get(
            "https://ws.audioscrobbler.com/2.0/",
            params=params,
        )

    # Raises an exception if the HTTP request was unsuccessful.
    response.raise_for_status()

    data = response.json()

    # Validates the API response.
    if not isinstance(data, dict):
        raise ValueError("Invalid Last.fm API response.")

    # Handles errors returned by the Last.fm API.
    if "error" in data:
        raise ValueError(data.get("message", "Last.fm API request failed."))

    return data


# Sends an authenticated request to the Last.fm API.
async def authenticated_api_request(
    session_key: str,
    method: str,
    params: dict[str, str] | None = None,
    client: httpx.AsyncClient | None = None,
) -> dict:
    request_params = {
        **(params or {}),
        "method": method,
        "api_key": settings.LASTFM_API_KEY,
        "sk": session_key,
    }

    request_params["api_sig"] = generate_api_signature(request_params)
    request_params["format"] = "json"

    return await make_api_request(request_params, client)


# Exchanges a Last.fm authentication token for a session key.
async def get_session(
    token: str,
    client: httpx.AsyncClient | None = None,
) -> tuple[str, str]:
    params = {
        "method": "auth.getSession",
        "api_key": settings.LASTFM_API_KEY,
        "token": token,
    }

    params["api_sig"] = generate_api_signature(params)
    params["format"] = "json"

    data = await make_api_request(params, client)

    # Validates the session data returned by Last.fm.
    session = data.get("session")

    if not isinstance(session, dict):
        raise ValueError("Invalid Last.fm session response.")

    session_key = session.get("key")

    if not isinstance(session_key, str) or not session_key:
        raise ValueError("Invalid Last.fm session key.")

    lastfm_username = session.get("name")

    if not isinstance(lastfm_username, str) or not lastfm_username:
        raise ValueError("Invalid Last.fm username.")

    return lastfm_username, session_key
