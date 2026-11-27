from sqlalchemy import Column, ForeignKey, Table

from app.database import Base

# Associates artists with genres.
artist_genres = Table(
    "artist_genres",
    Base.metadata,
    Column(
        "artist_id",
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Associates albums with genres.
album_genres = Table(
    "album_genres",
    Base.metadata,
    Column(
        "album_id",
        ForeignKey("albums.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Associates tracks with genres.
track_genres = Table(
    "track_genres",
    Base.metadata,
    Column(
        "track_id",
        ForeignKey("tracks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
