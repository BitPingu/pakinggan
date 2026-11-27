from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.genre import Genre
    from app.models.track import Track


# Represents an artist in the music library.
class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    metadata_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    albums: Mapped[list["Album"]] = relationship(back_populates="artist")
    tracks: Mapped[list["Track"]] = relationship(back_populates="artist")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="artist_genres",
        back_populates="artists",
    )
