from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.artist import Artist
    from app.models.genre import Genre
    from app.models.listening_history import ListeningHistory


# Represents a track belonging to an artist and optionally an album.
class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id"),
        nullable=False,
    )

    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("albums.id"),
        nullable=True,
    )

    artist: Mapped["Artist"] = relationship(back_populates="tracks")
    album: Mapped["Album"] = relationship(back_populates="tracks")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="track_genres",
        back_populates="tracks",
    )

    listening_history: Mapped[list["ListeningHistory"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
    )
