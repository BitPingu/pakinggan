from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.models.listening_history import ListeningHistory
from app.models.track import Track
from app.services.listening_history import (
    parse_lastfm_timestamp,
    sync_listening_history,
    sync_track_metadata_if_needed,
)


# Converts a Last.fm Unix timestamp into a UTC datetime.
def test_parse_lastfm_timestamp_returns_utc_datetime():
    result = parse_lastfm_timestamp("1795622400")

    assert result == datetime(2026, 11, 25, 16, 0, tzinfo=timezone.utc)
    assert result.tzinfo == timezone.utc


# Raises ValueError when the timestamp is not a valid Unix timestamp.
def test_parse_lastfm_timestamp_raises_value_error_for_invalid_timestamp():
    with pytest.raises(ValueError):
        parse_lastfm_timestamp("invalid")


# Raises ValueError when the timestamp is empty.
def test_parse_lastfm_timestamp_raises_value_error_for_empty_timestamp():
    with pytest.raises(ValueError):
        parse_lastfm_timestamp("")


# Imports a recently played track into listening history.
async def test_sync_listening_history_imports_tracks(db_session, user, track):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": "1795622400"},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                None,
                None,
                db_session.get(Track, track["id"]),
            ),
        ),
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 1
    assert len(history) == 1
    assert history[0].track_id == track["id"]
    assert history[0].played_at == datetime(2026, 11, 25, 16, 0, tzinfo=timezone.utc)


# Skips tracks that are currently playing.
async def test_sync_listening_history_skips_now_playing_tracks(db_session, user):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "@attr": {"nowplaying": "true"},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 0


# Returns zero when the Last.fm request returns no response.
async def test_sync_listening_history_returns_zero_without_response(db_session, user):
    with patch(
        "app.services.listening_history.make_user_lastfm_request",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_request:
        result = await sync_listening_history(db_session, user["id"])

    mock_request.assert_awaited_once()

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 0


# Normalizes a single track response into a list.
async def test_sync_listening_history_handles_single_track(db_session, user, track):
    lastfm_response = {
        "recenttracks": {
            "track": {
                "name": "Test Track",
                "artist": {"#text": "Test Artist"},
                "album": {"#text": "Test Album"},
                "date": {"uts": "1795622400"},
            }
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                None,
                None,
                db_session.get(Track, track["id"]),
            ),
        ),
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 1
    assert len(history) == 1
    assert history[0].track_id == track["id"]


# Skips tracks that do not have a listening timestamp.
async def test_sync_listening_history_skips_tracks_without_timestamp(db_session, user):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 0


# Imports multiple recently played tracks into listening history.
async def test_sync_listening_history_imports_multiple_tracks(db_session, user, track):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track 1",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": "1795622400"},
                },
                {
                    "name": "Test Track 2",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": "1795622460"},
                },
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                None,
                None,
                db_session.get(Track, track["id"]),
            ),
        ) as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 2
    assert len(history) == 2
    assert mock_resolve.call_count == 2
    assert all(entry.track_id == track["id"] for entry in history)


# Skips tracks that have an empty listening timestamp.
async def test_sync_listening_history_skips_tracks_with_empty_timestamp(
    db_session, user
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": ""},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 0


# Requests the user's 20 most recently played tracks from Last.fm.
async def test_sync_listening_history_uses_correct_request_parameters(db_session, user):
    with patch(
        "app.services.listening_history.make_user_lastfm_request",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_request:
        await sync_listening_history(db_session, user["id"])

    mock_request.assert_awaited_once_with(
        user_id=user["id"],
        method="user.getRecentTracks",
        db=db_session,
        params={
            "limit": "20",
            "page": "1",
        },
    )


# Requests the specified page of recently played tracks from Last.fm.
async def test_sync_listening_history_uses_specified_page(db_session, user):
    with patch(
        "app.services.listening_history.make_user_lastfm_request",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_request:
        await sync_listening_history(db_session, user["id"], page=2)

    mock_request.assert_awaited_once_with(
        user_id=user["id"],
        method="user.getRecentTracks",
        db=db_session,
        params={
            "limit": "20",
            "page": "2",
        },
    )


# Returns zero when Last.fm returns an empty track list.
async def test_sync_listening_history_handles_empty_track_list(db_session, user):
    lastfm_response = {"recenttracks": {"track": []}}

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 0


# Skips plays that have already been imported.
async def test_sync_listening_history_skips_duplicate_plays(db_session, user, track):
    played_at = datetime(2026, 11, 25, 16, 0, tzinfo=timezone.utc)

    # Creates an existing listening-history entry.
    existing_history = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=played_at,
    )

    db_session.add(existing_history)
    db_session.commit()

    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": "1795622400"},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                None,
                None,
                db_session.get(Track, track["id"]),
            ),
        ),
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 0
    assert len(history) == 1


# Returns zero when Last.fm returns invalid recent-tracks data.
@pytest.mark.parametrize("recent_tracks_data", [None, [], "invalid"])
async def test_sync_listening_history_handles_invalid_recent_tracks(
    db_session, user, recent_tracks_data
):
    lastfm_response = {"recenttracks": recent_tracks_data}

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()
    assert result == 0


# Skips malformed entries while importing valid tracks.
async def test_sync_listening_history_skips_malformed_track_entries(
    db_session, user, track
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                None,
                "invalid",
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "date": {"uts": "1795622400"},
                },
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                None,
                None,
                db_session.get(Track, track["id"]),
            ),
        ) as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 1
    assert len(history) == 1
    mock_resolve.assert_called_once()


# Skips tracks with non-numeric listening timestamps.
@pytest.mark.parametrize("timestamp", ["invalid", "12.5", "abc123"])
async def test_sync_listening_history_skips_invalid_timestamps(
    db_session, user, timestamp
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "date": {"uts": timestamp},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()
    assert result == 0


# Skips tracks with missing or invalid track and artist names.
@pytest.mark.parametrize(
    ("track_name", "artist"),
    [
        (None, {"#text": "Test Artist"}),
        ("", {"#text": "Test Artist"}),
        ("   ", {"#text": "Test Artist"}),
        ("Test Track", None),
        ("Test Track", "Test Artist"),
        ("Test Track", {"#text": ""}),
        ("Test Track", {"#text": "   "}),
    ],
)
async def test_sync_listening_history_skips_invalid_track_metadata(
    db_session, user, track_name, artist
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": track_name,
                    "artist": artist,
                    "date": {"uts": "1795622400"},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()
    assert result == 0


# Skips tracks with malformed date and artist structures.
@pytest.mark.parametrize(
    ("artist", "date"),
    [
        ("invalid", {"uts": "1795622400"}),
        ({"#text": "Test Artist"}, None),
        ({"#text": "Test Artist"}, "invalid"),
        ({"#text": "Test Artist"}, []),
    ],
)
async def test_sync_listening_history_skips_malformed_nested_data(
    db_session, user, artist, date
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": artist,
                    "date": date,
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch("app.services.listening_history.resolve_track_metadata") as mock_resolve,
    ):
        result = await sync_listening_history(db_session, user["id"])

    mock_resolve.assert_not_called()
    assert result == 0


# Synchronizes missing or stale metadata for all related entities.
async def test_sync_track_metadata_if_needed(db_session, artist, album, track):
    with (
        patch(
            "app.services.listening_history.needs_metadata_sync",
            return_value=True,
        ),
        patch(
            "app.services.listening_history.sync_artist_metadata",
            new_callable=AsyncMock,
        ) as mock_artist,
        patch(
            "app.services.listening_history.sync_album_metadata",
            new_callable=AsyncMock,
        ) as mock_album,
        patch(
            "app.services.listening_history.sync_track_metadata",
            new_callable=AsyncMock,
        ) as mock_track,
    ):
        await sync_track_metadata_if_needed(
            artist,
            album,
            track,
            db_session,
        )

    mock_artist.assert_awaited_once_with(artist, db_session)
    mock_album.assert_awaited_once_with(album, db_session)
    mock_track.assert_awaited_once_with(track, db_session)


# Skips synchronization when all related metadata is fresh.
async def test_sync_track_metadata_if_needed_skips_fresh_metadata(
    db_session, artist, album, track
):
    with (
        patch(
            "app.services.listening_history.needs_metadata_sync",
            return_value=False,
        ),
        patch(
            "app.services.listening_history.sync_artist_metadata",
            new_callable=AsyncMock,
        ) as mock_artist,
        patch(
            "app.services.listening_history.sync_album_metadata",
            new_callable=AsyncMock,
        ) as mock_album,
        patch(
            "app.services.listening_history.sync_track_metadata",
            new_callable=AsyncMock,
        ) as mock_track,
    ):
        await sync_track_metadata_if_needed(
            artist,
            album,
            track,
            db_session,
        )

    mock_artist.assert_not_awaited()
    mock_album.assert_not_awaited()
    mock_track.assert_not_awaited()


# Continues synchronization when a metadata API request fails.
async def test_sync_track_metadata_if_needed_handles_api_errors(
    db_session, artist, album, track
):
    with (
        patch(
            "app.services.listening_history.needs_metadata_sync",
            return_value=True,
        ),
        patch(
            "app.services.listening_history.sync_artist_metadata",
            new_callable=AsyncMock,
            side_effect=ValueError("Last.fm API error"),
        ) as mock_artist,
        patch(
            "app.services.listening_history.sync_album_metadata",
            new_callable=AsyncMock,
        ) as mock_album,
        patch(
            "app.services.listening_history.sync_track_metadata",
            new_callable=AsyncMock,
        ) as mock_track,
    ):
        await sync_track_metadata_if_needed(
            artist,
            album,
            track,
            db_session,
        )

    mock_artist.assert_awaited_once_with(artist, db_session)
    mock_album.assert_awaited_once_with(album, db_session)
    mock_track.assert_awaited_once_with(track, db_session)


# Synchronizes artist and track metadata when an album is unavailable.
async def test_sync_track_metadata_if_needed_without_album(db_session, artist, track):
    with (
        patch(
            "app.services.listening_history.needs_metadata_sync",
            return_value=True,
        ),
        patch(
            "app.services.listening_history.sync_artist_metadata",
            new_callable=AsyncMock,
        ) as mock_artist,
        patch(
            "app.services.listening_history.sync_album_metadata",
            new_callable=AsyncMock,
        ) as mock_album,
        patch(
            "app.services.listening_history.sync_track_metadata",
            new_callable=AsyncMock,
        ) as mock_track,
    ):
        await sync_track_metadata_if_needed(
            artist,
            None,
            track,
            db_session,
        )

    mock_artist.assert_awaited_once_with(artist, db_session)
    mock_album.assert_not_awaited()
    mock_track.assert_awaited_once_with(track, db_session)


# Imports listening history even when metadata synchronization fails.
async def test_sync_listening_history_imports_track_when_metadata_sync_fails(
    db_session, user, artist, album, track
):
    lastfm_response = {
        "recenttracks": {
            "track": [
                {
                    "name": "Test Track",
                    "artist": {"#text": "Test Artist"},
                    "album": {"#text": "Test Album"},
                    "date": {"uts": "1795622400"},
                }
            ]
        }
    }

    with (
        patch(
            "app.services.listening_history.make_user_lastfm_request",
            new_callable=AsyncMock,
            return_value=lastfm_response,
        ),
        patch(
            "app.services.listening_history.resolve_track_metadata",
            return_value=(
                artist,
                album,
                db_session.get(Track, track["id"]),
            ),
        ),
        patch(
            "app.services.listening_history.needs_metadata_sync",
            return_value=True,
        ),
        patch(
            "app.services.listening_history.sync_artist_metadata",
            new_callable=AsyncMock,
            side_effect=ValueError("Last.fm API error"),
        ),
        patch(
            "app.services.listening_history.sync_album_metadata",
            new_callable=AsyncMock,
        ),
        patch(
            "app.services.listening_history.sync_track_metadata",
            new_callable=AsyncMock,
        ),
    ):
        result = await sync_listening_history(db_session, user["id"])

    history = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .all()
    )

    assert result == 1
    assert len(history) == 1
    assert history[0].track_id == track["id"]
