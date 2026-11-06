from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackResponse, TrackUpdate

# track endpoints
router = APIRouter(
    prefix="/api/tracks",
    tags=["Tracks"],
)


# retrieve all tracks
@router.get("/", response_model=list[TrackResponse])
def get_tracks(db: Session = Depends(get_db)):
    tracks = db.query(Track).all()
    return tracks


# retrieve a single track
@router.get("/{track_id}", response_model=TrackResponse)
def get_track(track_id: int, db: Session = Depends(get_db)):
    # retrieve the track
    track = db.query(Track).filter(Track.id == track_id).first()

    # handle missing tracks
    if track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    # return the track
    return track


# create a track
@router.post("/", response_model=TrackResponse, status_code=201)
def create_track(track: TrackCreate, db: Session = Depends(get_db)):
    # check whether album exists
    db_album = db.query(Album).filter(Album.id == track.album_id).first()

    # handle missing albums
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # creates a new track object
    db_track = Track(
        title=track.title,
        duration=track.duration,
        album_id=track.album_id,
    )

    db.add(db_track)  # add it to the session
    db.commit()  # commit the transaction
    db.refresh(db_track)  # refresh the object

    # return in json
    return db_track


# update an existing track
@router.put("/{track_id}", response_model=TrackResponse)
def update_track(
    track_id: int,
    track: TrackUpdate,
    db: Session = Depends(get_db),
):
    # retrieve the track
    db_track = db.query(Track).filter(Track.id == track_id).first()

    # handle missing tracks
    if db_track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    # check whether album exists
    db_album = db.query(Album).filter(Album.id == track.album_id).first()

    # handle missing albums
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # update the fields
    db_track.title = track.title
    db_track.duration = track.duration
    db_track.album_id = track.album_id

    # save the changes
    db.commit()
    db.refresh(db_track)

    # return the updated track
    return db_track


# delete a track
@router.delete("/{track_id}", status_code=204)
def delete_track(track_id: int, db: Session = Depends(get_db)):
    # retrieve the track
    db_track = db.query(Track).filter(Track.id == track_id).first()

    # handle missing tracks
    if db_track is None:
        raise HTTPException(
            status_code=404,
            detail="Track not found",
        )

    # mark the track for deletion
    db.delete(db_track)

    # save the changes
    db.commit()
