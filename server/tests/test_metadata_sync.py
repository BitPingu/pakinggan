from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre
from app.models.track import Track
from app.services.metadata_sync import (
    ALBUM_METADATA_REFRESH_INTERVAL,
    ARTIST_METADATA_REFRESH_INTERVAL,
    TRACK_METADATA_REFRESH_INTERVAL,
    needs_metadata_sync,
    sync_album_metadata,
    sync_artist_metadata,
    sync_track_metadata,
)


# Requires synchronization when metadata has never been updated.
def test_needs_metadata_sync_without_timestamp():
    artist = Artist(name="Radiohead")

    assert needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    )


# Defines the expected metadata refresh intervals.
def test_metadata_refresh_intervals():
    assert ARTIST_METADATA_REFRESH_INTERVAL == timedelta(days=90)
    assert ALBUM_METADATA_REFRESH_INTERVAL == timedelta(days=180)
    assert TRACK_METADATA_REFRESH_INTERVAL == timedelta(days=90)


# Skips synchronization when metadata is still fresh.
def test_needs_metadata_sync_with_fresh_timestamp():
    artist = Artist(
        name="Radiohead",
        metadata_updated_at=datetime.now(timezone.utc),
    )

    assert not needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    )


# Requires synchronization when metadata reaches its refresh interval.
def test_needs_metadata_sync_at_refresh_threshold():
    artist = Artist(
        name="Radiohead",
        metadata_updated_at=(
            datetime.now(timezone.utc) - ARTIST_METADATA_REFRESH_INTERVAL
        ),
    )

    assert needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    )


# Requires synchronization when metadata is older than its refresh interval.
def test_needs_metadata_sync_with_stale_timestamp():
    artist = Artist(
        name="Radiohead",
        metadata_updated_at=(
            datetime.now(timezone.utc)
            - ARTIST_METADATA_REFRESH_INTERVAL
            - timedelta(days=1)
        ),
    )

    assert needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    )


# Handles timestamps without timezone information.
def test_needs_metadata_sync_with_naive_timestamp():
    artist = Artist(
        name="Radiohead",
        metadata_updated_at=(datetime.now(timezone.utc).replace(tzinfo=None)),
    )

    assert not needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    )


# Synchronizes an artist's metadata from Last.fm.
@pytest.mark.asyncio
async def test_sync_artist_metadata(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    # Mocks the Last.fm API responses.
    mock_info = AsyncMock(
        return_value={
            "artist": {
                "bio": {"summary": "English rock band."},
                "image": [{"#text": "radiohead.jpg", "size": "mega"}],
            }
        }
    )
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_top_tags",
        mock_top_tags,
    )

    result = await sync_artist_metadata(artist, db_session)

    assert result.biography == "English rock band."
    assert result.image_url == "radiohead.jpg"
    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]
    assert isinstance(result.metadata_updated_at, datetime)
    assert result.metadata_updated_at.tzinfo is not None

    mock_info.assert_awaited_once_with("Radiohead", None)
    mock_top_tags.assert_awaited_once_with("Radiohead", None)

    assert db_session.query(Genre).count() == 2


# Preserves existing artist metadata when Last.fm returns empty values.
@pytest.mark.asyncio
async def test_sync_artist_metadata_preserves_existing_values(
    db_session,
    monkeypatch,
):
    artist = Artist(
        name="Radiohead",
        biography="Existing biography.",
        image_url="existing.jpg",
    )
    db_session.add(artist)
    db_session.flush()

    # Associates an existing genre with the artist.
    existing_genre = Genre(name="alternative rock")
    artist.genres = [existing_genre]
    db_session.flush()

    # Mocks Last.fm responses without metadata.
    mock_info = AsyncMock(return_value={"artist": {}})
    mock_top_tags = AsyncMock(return_value={"toptags": {"tag": []}})

    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_top_tags",
        mock_top_tags,
    )

    result = await sync_artist_metadata(artist, db_session)

    assert result.biography == "Existing biography."
    assert result.image_url == "existing.jpg"
    assert [genre.name for genre in result.genres] == ["alternative rock"]
    assert isinstance(result.metadata_updated_at, datetime)
    assert result.metadata_updated_at.tzinfo is not None


# Preserves existing metadata when a Last.fm request fails.
@pytest.mark.asyncio
async def test_sync_artist_metadata_handles_api_failure(
    db_session,
    monkeypatch,
):
    artist = Artist(
        name="Radiohead",
        biography="Existing biography.",
        image_url="existing.jpg",
    )
    db_session.add(artist)
    db_session.flush()

    # Mocks an existing synchronization timestamp.
    previous_timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    artist.metadata_updated_at = previous_timestamp

    # Mocks a successful information request followed by an API failure.
    mock_info = AsyncMock(
        return_value={
            "artist": {
                "bio": {"summary": "Updated biography."},
                "image": [{"#text": "updated.jpg", "size": "mega"}],
            }
        }
    )
    mock_top_tags = AsyncMock(side_effect=Exception("Last.fm API error"))

    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_top_tags",
        mock_top_tags,
    )

    with pytest.raises(Exception, match="Last.fm API error"):
        await sync_artist_metadata(artist, db_session)

    assert artist.biography == "Existing biography."
    assert artist.image_url == "existing.jpg"
    assert artist.metadata_updated_at == previous_timestamp


# Replaces existing artist genres with updated Last.fm genres.
@pytest.mark.asyncio
async def test_sync_artist_metadata_replaces_genres(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    artist.genres = [Genre(name="rock")]
    db_session.add(artist)
    db_session.flush()

    mock_info = AsyncMock(return_value={"artist": {}})
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_artist_top_tags",
        mock_top_tags,
    )

    result = await sync_artist_metadata(artist, db_session)

    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]


# Synchronizes an album's metadata from Last.fm.
@pytest.mark.asyncio
async def test_sync_album_metadata(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    album = Album(title="OK Computer", artist=artist)
    db_session.add(album)
    db_session.flush()

    # Mocks the Last.fm API responses.
    mock_info = AsyncMock(
        return_value={
            "album": {
                "releasedate": "16 June 1997",
                "image": [{"#text": "ok-computer.jpg", "size": "mega"}],
            }
        }
    )
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_top_tags",
        mock_top_tags,
    )

    result = await sync_album_metadata(album, db_session)

    assert result.release_date == "16 June 1997"
    assert result.image_url == "ok-computer.jpg"
    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]
    assert isinstance(result.metadata_updated_at, datetime)
    assert result.metadata_updated_at.tzinfo is not None

    mock_info.assert_awaited_once_with("OK Computer", "Radiohead", None)
    mock_top_tags.assert_awaited_once_with("OK Computer", "Radiohead", None)

    assert db_session.query(Genre).count() == 2


# Preserves existing album metadata when Last.fm returns empty values.
@pytest.mark.asyncio
async def test_sync_album_metadata_preserves_existing_values(
    db_session,
    monkeypatch,
):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    album = Album(
        title="OK Computer",
        artist=artist,
        release_date="1997",
        image_url="existing.jpg",
    )
    album.genres = [Genre(name="alternative rock")]
    db_session.add(album)
    db_session.flush()

    mock_info = AsyncMock(return_value={"album": {}})
    mock_top_tags = AsyncMock(return_value={"toptags": {"tag": []}})

    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_top_tags",
        mock_top_tags,
    )

    result = await sync_album_metadata(album, db_session)

    assert result.release_date == "1997"
    assert result.image_url == "existing.jpg"
    assert [genre.name for genre in result.genres] == ["alternative rock"]
    assert isinstance(result.metadata_updated_at, datetime)


# Preserves existing album metadata when a Last.fm request fails.
@pytest.mark.asyncio
async def test_sync_album_metadata_handles_api_failure(
    db_session,
    monkeypatch,
):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    album = Album(
        title="OK Computer",
        artist=artist,
        release_date="1997",
        image_url="existing.jpg",
    )
    db_session.add(album)
    db_session.flush()

    previous_timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)
    album.metadata_updated_at = previous_timestamp

    mock_info = AsyncMock(
        return_value={
            "album": {
                "releasedate": "1998",
                "image": [{"#text": "updated.jpg", "size": "mega"}],
            }
        }
    )
    mock_top_tags = AsyncMock(side_effect=Exception("Last.fm API error"))

    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_top_tags",
        mock_top_tags,
    )

    with pytest.raises(Exception, match="Last.fm API error"):
        await sync_album_metadata(album, db_session)

    assert album.release_date == "1997"
    assert album.image_url == "existing.jpg"
    assert album.metadata_updated_at == previous_timestamp


# Replaces existing album genres with updated Last.fm genres.
@pytest.mark.asyncio
async def test_sync_album_metadata_replaces_genres(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    album = Album(title="OK Computer", artist=artist)
    album.genres = [Genre(name="rock")]
    db_session.add(album)
    db_session.flush()

    mock_info = AsyncMock(return_value={"album": {}})
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_album_top_tags",
        mock_top_tags,
    )

    result = await sync_album_metadata(album, db_session)

    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]


# Synchronizes a track's metadata from Last.fm.
@pytest.mark.asyncio
async def test_sync_track_metadata(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    album = Album(title="OK Computer", artist=artist)
    db_session.add(album)
    db_session.flush()

    track = Track(
        title="Paranoid Android",
        artist=artist,
        album=album,
        duration=383,
    )
    db_session.add(track)
    db_session.flush()

    # Mocks the Last.fm API responses.
    mock_info = AsyncMock(
        return_value={
            "track": {
                "wiki": {"summary": "A song from Radiohead's OK Computer."},
                "album": {
                    "image": [{"#text": "ok-computer.jpg", "size": "mega"}],
                },
            }
        }
    )
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_top_tags",
        mock_top_tags,
    )

    result = await sync_track_metadata(track, db_session)

    assert result.description == "A song from Radiohead's OK Computer."
    assert result.duration == 383
    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]
    assert isinstance(result.metadata_updated_at, datetime)
    assert result.metadata_updated_at.tzinfo is not None

    mock_info.assert_awaited_once_with("Paranoid Android", "Radiohead", None)
    mock_top_tags.assert_awaited_once_with("Paranoid Android", "Radiohead", None)

    assert db_session.query(Genre).count() == 2


# Preserves existing track metadata when Last.fm returns empty values.
@pytest.mark.asyncio
async def test_sync_track_metadata_preserves_existing_values(
    db_session,
    monkeypatch,
):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    track = Track(
        title="Paranoid Android",
        artist=artist,
        description="Existing description.",
        duration=383,
    )
    track.genres = [Genre(name="alternative rock")]
    db_session.add(track)
    db_session.flush()

    mock_info = AsyncMock(return_value={"track": {}})
    mock_top_tags = AsyncMock(return_value={"toptags": {"tag": []}})

    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_top_tags",
        mock_top_tags,
    )

    result = await sync_track_metadata(track, db_session)

    assert result.description == "Existing description."
    assert result.duration == 383
    assert [genre.name for genre in result.genres] == ["alternative rock"]
    assert isinstance(result.metadata_updated_at, datetime)


# Preserves existing track metadata when a Last.fm request fails.
@pytest.mark.asyncio
async def test_sync_track_metadata_handles_api_failure(
    db_session,
    monkeypatch,
):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    track = Track(
        title="Paranoid Android",
        artist=artist,
        description="Existing description.",
        duration=383,
    )
    db_session.add(track)
    db_session.flush()

    previous_timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc)

    track.metadata_updated_at = previous_timestamp

    mock_info = AsyncMock(
        return_value={
            "track": {
                "wiki": {"summary": "Updated description."},
            }
        }
    )
    mock_top_tags = AsyncMock(side_effect=Exception("Last.fm API error"))

    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_top_tags",
        mock_top_tags,
    )

    with pytest.raises(Exception, match="Last.fm API error"):
        await sync_track_metadata(track, db_session)

    assert track.description == "Existing description."
    assert track.duration == 383
    assert track.metadata_updated_at == previous_timestamp


# Replaces existing track genres with updated Last.fm genres.
@pytest.mark.asyncio
async def test_sync_track_metadata_replaces_genres(db_session, monkeypatch):
    artist = Artist(name="Radiohead")
    db_session.add(artist)
    db_session.flush()

    track = Track(title="Paranoid Android", artist=artist)
    track.genres = [Genre(name="rock")]
    db_session.add(track)
    db_session.flush()

    mock_info = AsyncMock(return_value={"track": {}})
    mock_top_tags = AsyncMock(
        return_value={
            "toptags": {
                "tag": [
                    {"name": "alternative rock"},
                    {"name": "art rock"},
                ]
            }
        }
    )

    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_info",
        mock_info,
    )
    monkeypatch.setattr(
        "app.services.metadata_sync.get_track_top_tags",
        mock_top_tags,
    )

    result = await sync_track_metadata(track, db_session)

    assert [genre.name for genre in result.genres] == [
        "alternative rock",
        "art rock",
    ]
