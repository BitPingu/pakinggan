from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.artist import Artist
    from app.models.genre import Genre
    from app.models.track import Track


# Represents an album belonging to an artist.
class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    metadata_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Each album must belong to an existing artist.
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)

    # Define relationships with the associated artist, tracks, and genres.
    artist: Mapped["Artist"] = relationship(back_populates="albums")
    tracks: Mapped[list["Track"]] = relationship(back_populates="album")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="album_genres",
        back_populates="albums",
    )
