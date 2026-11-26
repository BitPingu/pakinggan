import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.database import get_db
from app.models.listening_history import ListeningHistory
from app.models.track import Track
from app.models.user import User
from app.schemas.listening_history import ListeningHistoryResponse
from app.services.lastfm import get_user_lastfm_connection
from app.services.listening_history import sync_listening_history

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


# Imports recent listening history from the user's Last.fm account.
@router.post("/sync")
async def sync_user_listening_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Checks whether the user has connected a Last.fm account.
        if not get_user_lastfm_connection(current_user.id, db):
            raise HTTPException(
                status_code=400,
                detail="Last.fm account is not connected.",
            )

        # Imports recent plays from Last.fm.
        imported_count = await sync_listening_history(db, current_user.id)

        # Commits the imported listening-history entries.
        db.commit()

        return {"imported": imported_count}

    except (httpx.HTTPError, ValueError):
        # Rolls back changes if the Last.fm request fails.
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail="Failed to sync listening history from Last.fm.",
        )

    except SQLAlchemyError:
        # Rolls back changes if a database operation fails.
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save listening history.",
        )
