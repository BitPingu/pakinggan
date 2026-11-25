from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.listening_history import ListeningHistory


# Represents a track in an album.
class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[int | None] = mapped_column(nullable=True)

    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("albums.id"),
        nullable=True,
    )

    album: Mapped["Album"] = relationship(back_populates="tracks")

    listening_history: Mapped[list["ListeningHistory"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
    )
