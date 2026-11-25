from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackResponse, TrackUpdate

# Defines the API endpoints for managing tracks.
router = APIRouter(
    prefix="/api/tracks",
    tags=["Tracks"],
)


# Validates the artist and optional album associations.
def validate_track_associations(
    artist_id: int,
    album_id: int | None,
    db: Session,
) -> None:
    # Ensures the associated artist exists.
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # Ensures the associated album exists and belongs to the artist.
    if album_id is not None:
        db_album = db.query(Album).filter(Album.id == album_id).first()

        if db_album is None:
            raise HTTPException(
                status_code=404,
                detail="Album not found",
            )

        if db_album.artist_id != artist_id:
            raise HTTPException(
                status_code=400,
                detail="Album does not belong to the specified artist",
            )


# Retrieves all tracks.
@router.get("/", response_model=list[TrackResponse])
def get_tracks(db: Session = Depends(get_db)):
    tracks = db.query(Track).all()
    return tracks


# Retrieves a single track by ID.
@router.get("/{track_id}", response_model=TrackResponse)
def get_track(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()

    if track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    return track


# Creates a new track.
@router.post("/", response_model=TrackResponse, status_code=201)
def create_track(track: TrackCreate, db: Session = Depends(get_db)):
    # Validates the artist and optional album associations.
    validate_track_associations(
        artist_id=track.artist_id,
        album_id=track.album_id,
        db=db,
    )

    db_track = Track(
        title=track.title,
        duration=track.duration,
        artist_id=track.artist_id,
        album_id=track.album_id,
    )

    # Saves the new track to the database.
    db.add(db_track)
    db.commit()
    db.refresh(db_track)

    return db_track


# Updates an existing track.
@router.put("/{track_id}", response_model=TrackResponse)
def update_track(
    track_id: int,
    track: TrackUpdate,
    db: Session = Depends(get_db),
):
    db_track = db.query(Track).filter(Track.id == track_id).first()

    if db_track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    # Validates the artist and optional album associations.
    validate_track_associations(
        artist_id=track.artist_id,
        album_id=track.album_id,
        db=db,
    )

    db_track.title = track.title
    db_track.duration = track.duration
    db_track.artist_id = track.artist_id
    db_track.album_id = track.album_id

    # Saves the updated track to the database.
    db.commit()
    db.refresh(db_track)

    return db_track


# Deletes an existing track.
@router.delete("/{track_id}", status_code=204)
def delete_track(track_id: int, db: Session = Depends(get_db)):
    db_track = db.query(Track).filter(Track.id == track_id).first()

    if db_track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    # Removes the track from the database.
    db.delete(db_track)
    db.commit()
