from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.artist import Artist
    from app.models.track import Track


# Represents a music genre.
class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    artists: Mapped[list["Artist"]] = relationship(
        secondary="artist_genres",
        back_populates="genres",
    )
    albums: Mapped[list["Album"]] = relationship(
        secondary="album_genres",
        back_populates="genres",
    )
    tracks: Mapped[list["Track"]] = relationship(
        secondary="track_genres",
        back_populates="genres",
    )
