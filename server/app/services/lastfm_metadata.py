import re
from html import unescape

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


# Removes HTML markup and normalizes whitespace from text.
def clean_metadata_text(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None

    value = unescape(re.sub(r"<[^>]*>", "", value))
    value = " ".join(value.split())

    return value or None


# Extracts the largest available image URL from Last.fm image data.
def extract_image_url(images: list | None) -> str | None:
    if not isinstance(images, list):
        return None

    preferred_sizes = ["mega", "extralarge", "large", "medium", "small"]

    for size in preferred_sizes:
        for image in images:
            if isinstance(image, dict) and image.get("size") == size:
                url = image.get("#text")

                if isinstance(url, str) and url.strip():
                    return url.strip()

    return None


# Extracts and normalizes tag names from Last.fm top tags.
def extract_genres(data: dict) -> list[str]:
    if not isinstance(data, dict):
        return []

    top_tags = data.get("toptags", {})

    if not isinstance(top_tags, dict):
        return []

    tags = top_tags.get("tag", [])

    if isinstance(tags, dict):
        tags = [tags]

    if not isinstance(tags, list):
        return []

    genres = []
    seen = set()

    for tag in tags:
        if not isinstance(tag, dict):
            continue

        name = tag.get("name")

        if not isinstance(name, str):
            continue

        name = " ".join(name.split())
        normalized_name = name.casefold()

        if name and normalized_name not in seen:
            genres.append(name)
            seen.add(normalized_name)

    return genres


# Parses artist information and tags from Last.fm responses.
def parse_artist_metadata(info: dict, top_tags: dict) -> dict:
    if not isinstance(info, dict):
        info = {}

    artist = info.get("artist", {})

    if not isinstance(artist, dict):
        artist = {}

    bio = artist.get("bio", {})

    if not isinstance(bio, dict):
        bio = {}

    return {
        "biography": clean_metadata_text(bio.get("summary")),
        "image_url": extract_image_url(artist.get("image")),
        "genres": extract_genres(top_tags),
    }


# Parses album information and tags from Last.fm responses.
def parse_album_metadata(info: dict, top_tags: dict) -> dict:
    if not isinstance(info, dict):
        info = {}

    album = info.get("album", {})

    if not isinstance(album, dict):
        album = {}

    return {
        "release_date": clean_metadata_text(album.get("releasedate")),
        "image_url": extract_image_url(album.get("image")),
        "genres": extract_genres(top_tags),
    }


# Parses track information and tags from Last.fm responses.
def parse_track_metadata(info: dict, top_tags: dict) -> dict:
    if not isinstance(info, dict):
        info = {}

    track = info.get("track", {})

    if not isinstance(track, dict):
        track = {}

    album = track.get("album", {})

    if not isinstance(album, dict):
        album = {}

    return {
        "description": clean_metadata_text(track.get("wiki", {}).get("summary"))
        if isinstance(track.get("wiki"), dict)
        else None,
        "image_url": extract_image_url(album.get("image")),
        "genres": extract_genres(top_tags),
    }
