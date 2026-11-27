from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre
from app.models.track import Track
from app.schemas.lastfm import LastFMTrack


# Finds an existing artist or creates a new one.
def get_or_create_artist(name: str, db: Session) -> Artist:
    artist = (
        db.query(Artist).filter(func.lower(Artist.name) == name.strip().lower()).first()
    )

    if artist:
        return artist

    artist = Artist(name=name.strip())
    db.add(artist)
    db.flush()

    return artist


# Finds an existing album for an artist or creates a new one.
def get_or_create_album(title: str, artist_id: int, db: Session) -> Album:
    album = (
        db.query(Album)
        .filter(
            func.lower(Album.title) == title.strip().lower(),
            Album.artist_id == artist_id,
        )
        .first()
    )

    if album:
        return album

    album = Album(title=title.strip(), artist_id=artist_id)
    db.add(album)
    db.flush()

    return album


# Finds an existing track or creates a new one.
def get_or_create_track(
    title: str,
    artist_id: int,
    album_id: int | None,
    db: Session,
    duration: int | None = None,
) -> Track:
    query = db.query(Track).filter(
        func.lower(Track.title) == title.strip().lower(),
        Track.artist_id == artist_id,
    )

    if album_id is None:
        query = query.filter(Track.album_id.is_(None))
    else:
        query = query.filter(Track.album_id == album_id)

    track = query.first()

    if track:
        return track

    track = Track(
        title=title.strip(),
        artist_id=artist_id,
        album_id=album_id,
        duration=duration,
    )
    db.add(track)
    db.flush()

    return track


# Finds an existing genre or creates a new one.
def get_or_create_genre(name: str, db: Session) -> Genre:
    # Searches for an existing genre without considering capitalization.
    genre = (
        db.query(Genre).filter(func.lower(Genre.name) == name.strip().lower()).first()
    )

    # Returns the existing genre if one is found.
    if genre:
        return genre

    # Creates a new genre if one does not exist.
    genre = Genre(name=name.strip())
    db.add(genre)
    db.flush()

    return genre


# Associates an entity with its genres.
def update_entity_genres(
    entity: Artist | Album | Track,
    genre_names: list[str],
    db: Session,
) -> None:
    # Removes whitespace and duplicate genre names, ignoring capitalization.
    normalized_names = []
    seen_names = set()

    for name in genre_names:
        name = name.strip()
        normalized_name = name.casefold()

        if name and normalized_name not in seen_names:
            normalized_names.append(name)
            seen_names.add(normalized_name)

    # Preserves existing genres when no valid genres are provided.
    if not normalized_names:
        return

    # Finds or creates each genre and associates it with the entity.
    entity.genres = [get_or_create_genre(name, db) for name in normalized_names]


# Resolves Last.fm track metadata to database records.
def resolve_track_metadata(
    metadata: LastFMTrack,
    db: Session,
) -> tuple[Artist, Album | None, Track]:
    artist = get_or_create_artist(metadata.artist, db)

    album = None

    if metadata.album and metadata.album.strip():
        album = get_or_create_album(metadata.album, artist.id, db)

    track = get_or_create_track(
        metadata.name,
        artist.id,
        album.id if album else None,
        db,
    )

    return artist, album, track
