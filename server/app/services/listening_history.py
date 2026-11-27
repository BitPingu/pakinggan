from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.listening_history import ListeningHistory
from app.schemas.lastfm import LastFMTrack
from app.services.lastfm import make_user_lastfm_request
from app.services.metadata_sync import (
    ALBUM_METADATA_REFRESH_INTERVAL,
    ARTIST_METADATA_REFRESH_INTERVAL,
    TRACK_METADATA_REFRESH_INTERVAL,
    needs_metadata_sync,
    sync_album_metadata,
    sync_artist_metadata,
    sync_track_metadata,
)
from app.services.music_metadata import resolve_track_metadata


# Converts a Last.fm Unix timestamp into a timezone-aware datetime.
def parse_lastfm_timestamp(timestamp: str) -> datetime:
    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)


# Synchronizes missing or stale metadata for a track and its related entities.
async def sync_track_metadata_if_needed(
    artist,
    album,
    track,
    db: Session,
) -> None:
    if artist and needs_metadata_sync(
        artist,
        ARTIST_METADATA_REFRESH_INTERVAL,
    ):
        try:
            await sync_artist_metadata(artist, db)
        except (httpx.HTTPError, ValueError):
            pass

    if album and needs_metadata_sync(
        album,
        ALBUM_METADATA_REFRESH_INTERVAL,
    ):
        try:
            await sync_album_metadata(album, db)
        except (httpx.HTTPError, ValueError):
            pass

    if (
        artist
        and track
        and needs_metadata_sync(
            track,
            TRACK_METADATA_REFRESH_INTERVAL,
        )
    ):
        try:
            await sync_track_metadata(track, db)
        except (httpx.HTTPError, ValueError):
            pass


# Imports recent listening history from Last.fm.
async def sync_listening_history(
    db: Session,
    user_id: int,
    page: int = 1,
) -> int:
    # Fetches the user's 20 most recently played tracks.
    response = await make_user_lastfm_request(
        user_id=user_id,
        method="user.getRecentTracks",
        db=db,
        params={
            "limit": "20",
            "page": str(page),
        },
    )

    # Returns zero if the Last.fm request fails or no connection exists.
    if not response:
        return 0

    # Extracts the recently played tracks from the API response.
    recent_tracks_data = response.get("recenttracks")

    if not isinstance(recent_tracks_data, dict):
        return 0

    recent_tracks = recent_tracks_data.get("track", [])

    # Normalizes a single track response into a list.
    if isinstance(recent_tracks, dict):
        recent_tracks = [recent_tracks]

    # Returns zero if the track collection is invalid.
    if not isinstance(recent_tracks, list):
        return 0

    imported_count = 0

    for raw_track in recent_tracks:
        # Skips entries that are not valid track objects.
        if not isinstance(raw_track, dict):
            continue

        # Skips tracks that are currently playing.
        attributes = raw_track.get("@attr", {}) or {}

        if isinstance(attributes, dict) and attributes.get("nowplaying") == "true":
            continue

        # Extracts the track and artist names.
        track_name = raw_track.get("name")
        artist = raw_track.get("artist")
        artist_name = artist.get("#text") if isinstance(artist, dict) else None

        # Skips tracks with missing or empty names.
        if not isinstance(track_name, str) or not track_name.strip():
            continue

        if not isinstance(artist_name, str) or not artist_name.strip():
            continue

        # Extracts the Unix timestamp from the track's date information.
        date = raw_track.get("date")

        if not isinstance(date, dict):
            continue

        timestamp = date.get("uts")

        # Skips tracks with missing or invalid listening timestamps.
        if not isinstance(timestamp, str) or not timestamp.isdigit():
            continue

        # Extracts the album name when available.
        album = raw_track.get("album")
        album_name = album.get("#text") if isinstance(album, dict) else None

        if not isinstance(album_name, str) or not album_name.strip():
            album_name = None

        # Converts the raw Last.fm response into a validated track schema.
        metadata = LastFMTrack(
            name=track_name,
            artist=artist_name,
            album=album_name or None,
            url=raw_track.get("url"),
            played_at=date.get("#text"),
            uts=timestamp,
        )

        # Resolves the track metadata to existing or newly created records.
        artist, album, track = resolve_track_metadata(metadata, db)

        # Converts the Last.fm timestamp into a timezone-aware datetime.
        played_at = parse_lastfm_timestamp(metadata.uts)

        # Skips plays that have already been imported.
        existing_history = (
            db.query(ListeningHistory)
            .filter(
                ListeningHistory.user_id == user_id,
                ListeningHistory.track_id == track.id,
                ListeningHistory.played_at == played_at,
            )
            .first()
        )

        if existing_history:
            continue

        # Synchronizes missing or stale music metadata.
        await sync_track_metadata_if_needed(artist, album, track, db)

        # Creates a listening-history entry for the played track.
        history = ListeningHistory(
            user_id=user_id,
            track_id=track.id,
            played_at=played_at,
        )

        db.add(history)
        imported_count += 1

    # Flushes the imported listening-history entries to the database.
    db.flush()

    return imported_count
