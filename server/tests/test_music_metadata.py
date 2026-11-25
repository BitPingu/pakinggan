from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.schemas.lastfm import LastFMTrack
from app.services.music_metadata import (
    get_or_create_album,
    get_or_create_artist,
    get_or_create_track,
    resolve_track_metadata,
)


# Creates an artist when one does not exist.
def test_get_or_create_artist_creates_artist(db_session):
    artist = get_or_create_artist("Radiohead", db_session)

    assert artist.id is not None
    assert artist.name == "Radiohead"

    assert db_session.query(Artist).count() == 1


# Returns an existing artist instead of creating a duplicate.
def test_get_or_create_artist_returns_existing_artist(db_session):
    existing_artist = Artist(name="Radiohead")
    db_session.add(existing_artist)
    db_session.flush()

    artist = get_or_create_artist("Radiohead", db_session)

    assert artist.id == existing_artist.id
    assert db_session.query(Artist).count() == 1


# Matches artist names without considering capitalization.
def test_get_or_create_artist_case_insensitive(db_session):
    existing_artist = Artist(name="Radiohead")
    db_session.add(existing_artist)
    db_session.flush()

    artist = get_or_create_artist("radiohead", db_session)

    assert artist.id == existing_artist.id
    assert artist.name == "Radiohead"
    assert db_session.query(Artist).count() == 1


# Removes surrounding whitespace from new artist names.
def test_get_or_create_artist_strips_whitespace(db_session):
    artist = get_or_create_artist("  Radiohead  ", db_session)

    assert artist.name == "Radiohead"


# Creates an album when one does not exist.
def test_get_or_create_album_creates_album(db_session, artist):
    album = get_or_create_album("OK Computer", artist["id"], db_session)

    assert album.id is not None
    assert album.title == "OK Computer"
    assert album.artist_id == artist["id"]

    assert db_session.query(Album).count() == 1


# Returns an existing album instead of creating a duplicate.
def test_get_or_create_album_returns_existing_album(db_session, album):
    existing_album = get_or_create_album(
        "OK Computer",
        album["artist_id"],
        db_session,
    )

    assert existing_album.id == album["id"]
    assert db_session.query(Album).count() == 1


# Matches album titles without considering capitalization.
def test_get_or_create_album_case_insensitive(db_session, artist):
    existing_album = Album(title="OK Computer", artist_id=artist["id"])
    db_session.add(existing_album)
    db_session.flush()

    album = get_or_create_album("ok computer", artist["id"], db_session)

    assert album.id == existing_album.id
    assert album.title == "OK Computer"
    assert db_session.query(Album).count() == 1


# Allows albums with the same title to belong to different artists.
def test_get_or_create_album_different_artists(db_session, artist):
    another_artist = Artist(name="The Beatles")
    db_session.add(another_artist)
    db_session.flush()

    first_album = get_or_create_album("Greatest Hits", artist["id"], db_session)
    second_album = get_or_create_album(
        "Greatest Hits",
        another_artist.id,
        db_session,
    )

    assert first_album.id != second_album.id
    assert first_album.artist_id != second_album.artist_id
    assert db_session.query(Album).count() == 2


# Creates a track when one does not exist.
def test_get_or_create_track_creates_track(db_session, album):
    track = get_or_create_track(
        "Paranoid Android",
        album["artist_id"],
        album["id"],
        db_session,
        duration=383,
    )

    assert track.id is not None
    assert track.title == "Paranoid Android"
    assert track.artist_id == album["artist_id"]
    assert track.album_id == album["id"]
    assert track.duration == 383

    assert db_session.query(Track).count() == 1


# Returns an existing track instead of creating a duplicate.
def test_get_or_create_track_returns_existing_track(db_session, track):
    existing_track = get_or_create_track(
        "Paranoid Android",
        track["artist_id"],
        track["album_id"],
        db_session,
        duration=383,
    )

    assert existing_track.id == track["id"]
    assert db_session.query(Track).count() == 1


# Matches track titles without considering capitalization.
def test_get_or_create_track_case_insensitive(db_session, album):
    existing_track = Track(
        title="Paranoid Android",
        artist_id=album["artist_id"],
        album_id=album["id"],
        duration=383,
    )
    db_session.add(existing_track)
    db_session.flush()

    track = get_or_create_track(
        "paranoid android",
        album["artist_id"],
        album["id"],
        db_session,
    )

    assert track.id == existing_track.id
    assert track.title == "Paranoid Android"
    assert db_session.query(Track).count() == 1


# Creates separate track records for different albums.
def test_get_or_create_track_different_albums(db_session, artist, album):
    another_album = Album(
        title="The Best Of",
        artist_id=artist["id"],
    )
    db_session.add(another_album)
    db_session.flush()

    first_track = get_or_create_track(
        "Creep",
        artist["id"],
        album["id"],
        db_session,
    )
    second_track = get_or_create_track(
        "Creep",
        artist["id"],
        another_album.id,
        db_session,
    )

    assert first_track.id != second_track.id
    assert first_track.album_id != second_track.album_id
    assert db_session.query(Track).count() == 2


# Creates a track without an associated album.
def test_get_or_create_track_without_album(db_session, artist):
    track = get_or_create_track(
        "Creep",
        artist["id"],
        None,
        db_session,
    )

    assert track.id is not None
    assert track.album_id is None
    assert track.artist_id == artist["id"]


# Reuses a track without an album.
def test_get_or_create_track_existing_without_album(db_session, artist):
    existing_track = Track(
        title="Creep",
        artist_id=artist["id"],
        album_id=None,
    )
    db_session.add(existing_track)
    db_session.flush()

    track = get_or_create_track(
        "Creep",
        artist["id"],
        None,
        db_session,
    )

    assert track.id == existing_track.id
    assert db_session.query(Track).count() == 1


# Preserves the existing duration when a track is found.
def test_get_or_create_track_preserves_existing_duration(db_session, track):
    existing_track = get_or_create_track(
        "Paranoid Android",
        track["artist_id"],
        track["album_id"],
        db_session,
        duration=400,
    )

    assert existing_track.id == track["id"]
    assert existing_track.duration == 383


# Resolves metadata and creates all associated records.
def test_resolve_track_metadata_creates_records(db_session):
    metadata = LastFMTrack(
        name="Paranoid Android",
        artist="Radiohead",
        album="OK Computer",
    )

    artist, album, track = resolve_track_metadata(metadata, db_session)

    assert artist.name == "Radiohead"
    assert album.title == "OK Computer"
    assert track.title == "Paranoid Android"
    assert track.artist_id == artist.id
    assert track.album_id == album.id


# Reuses existing records when resolving the same metadata.
def test_resolve_track_metadata_reuses_records(db_session):
    metadata = LastFMTrack(
        name="Paranoid Android",
        artist="Radiohead",
        album="OK Computer",
    )

    first_result = resolve_track_metadata(metadata, db_session)
    second_result = resolve_track_metadata(metadata, db_session)

    assert first_result[0].id == second_result[0].id
    assert first_result[1].id == second_result[1].id
    assert first_result[2].id == second_result[2].id

    assert db_session.query(Artist).count() == 1
    assert db_session.query(Album).count() == 1
    assert db_session.query(Track).count() == 1


# Resolves metadata for a track without an album.
def test_resolve_track_metadata_without_album(db_session):
    metadata = LastFMTrack(
        name="Creep",
        artist="Radiohead",
    )

    artist, album, track = resolve_track_metadata(metadata, db_session)

    assert artist.name == "Radiohead"
    assert album is None
    assert track.title == "Creep"
    assert track.artist_id == artist.id
    assert track.album_id is None


# Treats a whitespace-only album name as missing.
def test_resolve_track_metadata_blank_album(db_session):
    metadata = LastFMTrack(
        name="Creep",
        artist="Radiohead",
        album="   ",
    )

    artist, album, track = resolve_track_metadata(metadata, db_session)

    assert artist.name == "Radiohead"
    assert album is None
    assert track.album_id is None
