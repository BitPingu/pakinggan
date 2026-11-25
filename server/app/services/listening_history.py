from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.listening_history import ListeningHistory
from app.schemas.lastfm import LastFMTrack
from app.services.lastfm import make_user_lastfm_request
from app.services.music_metadata import resolve_track_metadata


# Converts a Last.fm Unix timestamp into a timezone-aware datetime.
def parse_lastfm_timestamp(timestamp: str) -> datetime:
    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)


# Imports recent listening history from Last.fm.
async def sync_listening_history(
    db: Session,
    user_id: int,
) -> int:
    # Fetches the user's 20 most recently played tracks.
    response = await make_user_lastfm_request(
        user_id=user_id,
        method="user.getRecentTracks",
        db=db,
        params={"limit": "20"},
    )

    # Returns zero if the Last.fm request fails or no connection exists.
    if not response:
        return 0

    # Extracts the recently played tracks from the API response.
    recent_tracks = response.get("recenttracks", {}).get("track", [])

    # Normalizes a single track response into a list.
    if isinstance(recent_tracks, dict):
        recent_tracks = [recent_tracks]

    imported_count = 0

    for raw_track in recent_tracks:
        # Skips tracks that are currently playing.
        attributes = raw_track.get("@attr", {}) or {}

        if attributes.get("nowplaying") == "true":
            continue

        # Extracts the Unix timestamp from the track's date information.
        date = raw_track.get("date", {}) or {}
        timestamp = date.get("uts")

        # Skips tracks without a listening timestamp.
        if not timestamp:
            continue

        # Converts the raw Last.fm response into a validated track schema.
        metadata = LastFMTrack(
            name=raw_track["name"],
            artist=raw_track["artist"]["#text"],
            album=raw_track.get("album", {}).get("#text") or None,
            url=raw_track.get("url"),
            played_at=date.get("#text"),
            uts=timestamp,
        )

        # Resolves the track metadata to existing or newly created records.
        _, _, track = resolve_track_metadata(metadata, db)

        # Creates a listening-history entry for the played track.
        history = ListeningHistory(
            user_id=user_id,
            track_id=track.id,
            played_at=parse_lastfm_timestamp(metadata.uts),
        )

        db.add(history)
        imported_count += 1

    # Flushes the imported listening-history entries to the database.
    db.flush()

    return imported_count
