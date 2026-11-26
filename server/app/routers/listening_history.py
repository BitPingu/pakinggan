from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.database import get_db
from app.models.listening_history import ListeningHistory
from app.models.track import Track
from app.models.user import User
from app.schemas.listening_history import ListeningHistoryResponse

# Defines the API endpoints for managing listening history.
router = APIRouter(
    prefix="/api/listening-history",
    tags=["Listening History"],
)


# Retrieves the authenticated user's listening history.
@router.get("/", response_model=list[ListeningHistoryResponse])
def get_listening_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = (
        db.query(ListeningHistory)
        .filter(ListeningHistory.user_id == current_user.id)
        .options(
            joinedload(ListeningHistory.track).joinedload(Track.artist),
            joinedload(ListeningHistory.track).joinedload(Track.album),
        )
        .order_by(
            ListeningHistory.played_at.desc(),
            ListeningHistory.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return history
