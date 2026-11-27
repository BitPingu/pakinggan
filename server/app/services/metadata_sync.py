from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
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
from app.services.music_metadata import update_entity_genres


# Synchronizes an artist's metadata using Last.fm.
async def sync_artist_metadata(
    artist: Artist,
    db: Session,
    client: httpx.AsyncClient | None = None,
) -> Artist:
    # Retrieves artist information and popular tags from Last.fm.
    info = await get_artist_info(artist.name, client)
    top_tags = await get_artist_top_tags(artist.name, client)

    # Parses the responses into normalized metadata.
    metadata = parse_artist_metadata(info, top_tags)

    # Updates metadata fields when Last.fm provides values.
    if metadata["biography"]:
        artist.biography = metadata["biography"]

    if metadata["image_url"]:
        artist.image_url = metadata["image_url"]

    # Updates genre associations when Last.fm provides genres.
    if metadata["genres"]:
        update_entity_genres(artist, metadata["genres"], db)

    # Records when the metadata was successfully synchronized.
    artist.metadata_updated_at = datetime.now(timezone.utc)

    db.flush()

    return artist


# Synchronizes an album's metadata using Last.fm.
async def sync_album_metadata(
    album: Album,
    db: Session,
    client: httpx.AsyncClient | None = None,
) -> Album:
    # Retrieves album information and popular tags from Last.fm.
    info = await get_album_info(album.title, album.artist.name, client)
    top_tags = await get_album_top_tags(album.title, album.artist.name, client)

    # Parses the responses into normalized metadata.
    metadata = parse_album_metadata(info, top_tags)

    # Updates metadata fields when Last.fm provides values.
    if metadata["release_date"]:
        album.release_date = metadata["release_date"]

    if metadata["image_url"]:
        album.image_url = metadata["image_url"]

    # Updates genre associations when Last.fm provides genres.
    if metadata["genres"]:
        update_entity_genres(album, metadata["genres"], db)

    # Records when the metadata was successfully synchronized.
    album.metadata_updated_at = datetime.now(timezone.utc)

    db.flush()

    return album


# Synchronizes a track's metadata using Last.fm.
async def sync_track_metadata(
    track: Track,
    db: Session,
    client: httpx.AsyncClient | None = None,
) -> Track:
    # Retrieves track information and popular tags from Last.fm.
    info = await get_track_info(track.title, track.artist.name, client)
    top_tags = await get_track_top_tags(track.title, track.artist.name, client)

    # Parses the responses into normalized metadata.
    metadata = parse_track_metadata(info, top_tags)

    # Updates metadata fields when Last.fm provides values.
    if metadata["description"]:
        track.description = metadata["description"]

    # Updates genre associations when Last.fm provides genres.
    if metadata["genres"]:
        update_entity_genres(track, metadata["genres"], db)

    # Records when the metadata was successfully synchronized.
    track.metadata_updated_at = datetime.now(timezone.utc)

    db.flush()

    return track
