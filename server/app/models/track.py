from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[int | None] = mapped_column(nullable=True)

    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"), nullable=False)

    album: Mapped["Album"] = relationship(back_populates="tracks")

