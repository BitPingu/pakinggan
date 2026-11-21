from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.artist import Artist
    from app.models.track import Track


# Represents an album belonging to an artist.
class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Each album must belong to an existing artist.
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False)

    # Define relationships with the associated artist and tracks.
    artist: Mapped["Artist"] = relationship(back_populates="albums")
    tracks: Mapped[list["Track"]] = relationship(back_populates="album")
