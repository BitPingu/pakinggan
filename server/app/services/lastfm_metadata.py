import httpx

from app.core.config import settings
from app.core.lastfm import make_api_request


# Retrieves artist information from Last.fm.
async def get_artist_info(
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "artist.getInfo",
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )


# Retrieves an artist's most popular tags from Last.fm.
async def get_artist_top_tags(
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "artist.getTopTags",
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )


# Retrieves album information from Last.fm.
async def get_album_info(
    album_name: str,
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "album.getInfo",
            "album": album_name,
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )


# Retrieves an album's most popular tags from Last.fm.
async def get_album_top_tags(
    album_name: str,
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "album.getTopTags",
            "album": album_name,
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )


# Retrieves track information from Last.fm.
async def get_track_info(
    track_name: str,
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "track.getInfo",
            "track": track_name,
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )


# Retrieves a track's most popular tags from Last.fm.
async def get_track_top_tags(
    track_name: str,
    artist_name: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    return await make_api_request(
        {
            "method": "track.getTopTags",
            "track": track_name,
            "artist": artist_name,
            "api_key": settings.LASTFM_API_KEY,
            "format": "json",
        },
        client,
    )
