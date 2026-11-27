import httpx
import pytest

from app.core.config import settings
from app.services.lastfm_metadata import (
    get_album_info,
    get_album_top_tags,
    get_artist_info,
    get_artist_top_tags,
    get_track_info,
    get_track_top_tags,
    parse_album_metadata,
    parse_artist_metadata,
    parse_track_metadata,
)


# Tests that artist information is retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_artist_info(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "artist.getInfo"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "artist": {
                    "name": "Radiohead",
                    "bio": {"summary": "English rock band."},
                    "image": [
                        {"#text": "small.jpg", "size": "small"},
                        {"#text": "large.jpg", "size": "large"},
                        {"#text": "mega.jpg", "size": "mega"},
                    ],
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_artist_info("Radiohead", client)

    assert data["artist"]["name"] == "Radiohead"
    assert data["artist"]["bio"]["summary"] == "English rock band."
    assert data["artist"]["image"][2]["#text"] == "mega.jpg"


# Tests that an artist's top tags are retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_artist_top_tags(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "artist.getTopTags"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "toptags": {
                    "tag": [
                        {"name": "alternative rock", "count": 100},
                        {"name": "art rock", "count": 80},
                    ]
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_artist_top_tags("Radiohead", client)

    tags = data["toptags"]["tag"]

    assert len(tags) == 2
    assert tags[0]["name"] == "alternative rock"
    assert tags[1]["name"] == "art rock"


# Tests that album information is retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_album_info(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "album.getInfo"
        assert params["album"] == "OK Computer"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "album": {
                    "name": "OK Computer",
                    "artist": "Radiohead",
                    "releasedate": "16 June 1997",
                    "image": [
                        {"#text": "small.jpg", "size": "small"},
                        {"#text": "large.jpg", "size": "large"},
                        {"#text": "mega.jpg", "size": "mega"},
                    ],
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_album_info("OK Computer", "Radiohead", client)

    assert data["album"]["name"] == "OK Computer"
    assert data["album"]["artist"] == "Radiohead"


# Tests that an album's top tags are retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_album_top_tags(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "album.getTopTags"
        assert params["album"] == "OK Computer"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "toptags": {
                    "tag": [
                        {"name": "alternative rock", "count": 100},
                        {"name": "art rock", "count": 80},
                    ]
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_album_top_tags("OK Computer", "Radiohead", client)

    tags = data["toptags"]["tag"]

    assert len(tags) == 2
    assert tags[0]["name"] == "alternative rock"
    assert tags[1]["name"] == "art rock"


# Tests that track information is retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_track_info(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "track.getInfo"
        assert params["track"] == "Paranoid Android"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "track": {
                    "name": "Paranoid Android",
                    "artist": {"name": "Radiohead"},
                    "duration": "383000",
                    "wiki": {"summary": "A song from Radiohead's OK Computer."},
                    "album": {
                        "title": "OK Computer",
                        "image": [
                            {"#text": "small.jpg", "size": "small"},
                            {"#text": "large.jpg", "size": "large"},
                            {"#text": "mega.jpg", "size": "mega"},
                        ],
                    },
                },
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_track_info("Paranoid Android", "Radiohead", client)

    assert data["track"]["name"] == "Paranoid Android"
    assert data["track"]["artist"]["name"] == "Radiohead"
    assert data["track"]["duration"] == "383000"


# Tests that a track's top tags are retrieved correctly from Last.fm.
@pytest.mark.asyncio
async def test_get_track_top_tags(monkeypatch):
    monkeypatch.setattr(settings, "LASTFM_API_KEY", "test_api_key")

    async def mock_handler(request):
        params = dict(request.url.params)

        assert params["method"] == "track.getTopTags"
        assert params["track"] == "Paranoid Android"
        assert params["artist"] == "Radiohead"
        assert params["api_key"] == "test_api_key"
        assert params["format"] == "json"

        return httpx.Response(
            200,
            json={
                "toptags": {
                    "tag": [
                        {"name": "alternative rock", "count": 100},
                        {"name": "progressive rock", "count": 80},
                    ]
                }
            },
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        data = await get_track_top_tags("Paranoid Android", "Radiohead", client)

    tags = data["toptags"]["tag"]

    assert len(tags) == 2
    assert tags[0]["name"] == "alternative rock"
    assert tags[1]["name"] == "progressive rock"


# Tests that artist metadata is parsed correctly.
def test_parse_artist_metadata():
    info = {
        "artist": {
            "name": "Radiohead",
            "bio": {
                "summary": (
                    "English rock band. <a href='https://example.com'>Read more</a>"
                )
            },
            "image": [
                {"#text": "small.jpg", "size": "small"},
                {"#text": "large.jpg", "size": "large"},
                {"#text": "mega.jpg", "size": "mega"},
            ],
        }
    }

    top_tags = {
        "toptags": {
            "tag": [
                {"name": "alternative rock", "count": 100},
                {"name": "art rock", "count": 80},
                {"name": "Alternative Rock", "count": 50},
            ]
        }
    }

    metadata = parse_artist_metadata(info, top_tags)

    assert metadata == {
        "biography": "English rock band. Read more",
        "image_url": "mega.jpg",
        "genres": ["alternative rock", "art rock"],
    }


# Tests that album metadata is parsed correctly.
def test_parse_album_metadata():
    info = {
        "album": {
            "name": "OK Computer",
            "artist": "Radiohead",
            "releasedate": "16 June 1997",
            "image": [
                {"#text": "small.jpg", "size": "small"},
                {"#text": "large.jpg", "size": "large"},
                {"#text": "mega.jpg", "size": "mega"},
            ],
        }
    }

    top_tags = {
        "toptags": {
            "tag": [
                {"name": "alternative rock", "count": 100},
                {"name": "art rock", "count": 80},
                {"name": "Alternative Rock", "count": 50},
            ]
        }
    }

    metadata = parse_album_metadata(info, top_tags)

    assert metadata == {
        "release_date": "16 June 1997",
        "image_url": "mega.jpg",
        "genres": ["alternative rock", "art rock"],
    }


# Tests that track metadata is parsed correctly.
def test_parse_track_metadata():
    info = {
        "track": {
            "name": "Paranoid Android",
            "wiki": {
                "summary": (
                    "A song from Radiohead's "
                    "<a href='https://example.com'>OK Computer</a>."
                )
            },
            "album": {
                "title": "OK Computer",
                "image": [
                    {"#text": "small.jpg", "size": "small"},
                    {"#text": "large.jpg", "size": "large"},
                    {"#text": "mega.jpg", "size": "mega"},
                ],
            },
        }
    }

    top_tags = {
        "toptags": {
            "tag": [
                {"name": "alternative rock", "count": 100},
                {"name": "progressive rock", "count": 80},
                {"name": "Alternative Rock", "count": 50},
            ]
        }
    }

    metadata = parse_track_metadata(info, top_tags)

    assert metadata == {
        "description": "A song from Radiohead's OK Computer.",
        "image_url": "mega.jpg",
        "genres": ["alternative rock", "progressive rock"],
    }


# Tests that metadata parsers handle malformed responses safely.
@pytest.mark.parametrize(
    ("parser", "info", "expected"),
    [
        (
            parse_artist_metadata,
            None,
            {"biography": None, "image_url": None, "genres": []},
        ),
        (
            parse_album_metadata,
            "invalid",
            {"release_date": None, "image_url": None, "genres": []},
        ),
        (
            parse_track_metadata,
            [],
            {"description": None, "image_url": None, "genres": []},
        ),
    ],
)
def test_parse_metadata_with_invalid_info(parser, info, expected):
    assert parser(info, {}) == expected
