from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.user import User


# Represents an individual track play in a user's listening history.
class ListeningHistory(Base):
    __tablename__ = "listening_history"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "track_id",
            "played_at",
            name="uq_listening_history_user_track_played_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="listening_history")
    track: Mapped["Track"] = relationship(back_populates="listening_history")
