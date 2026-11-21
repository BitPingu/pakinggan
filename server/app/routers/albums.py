from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.schemas.album import AlbumCreate, AlbumResponse, AlbumUpdate
from app.schemas.track import TrackResponse

# Defines the API endpoints for managing albums.
router = APIRouter(
    prefix="/api/albums",
    tags=["Albums"],
)


# Retrieves all albums.
@router.get("/", response_model=list[AlbumResponse])
def get_albums(db: Session = Depends(get_db)):
    albums = db.query(Album).all()
    return albums


# Retrieves a single album by ID.
@router.get("/{album_id}", response_model=AlbumResponse)
def get_album(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id).first()

    if album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    return album


# Creates a new album.
@router.post("/", response_model=AlbumResponse, status_code=201)
def create_album(album: AlbumCreate, db: Session = Depends(get_db)):
    # Ensures the associated artist exists.
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    db_album = Album(
        title=album.title,
        artist_id=album.artist_id,
    )

    # Saves the new album to the database.
    db.add(db_album)
    db.commit()
    db.refresh(db_album)

    return db_album


# Updates an existing album.
@router.put("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: int,
    album: AlbumUpdate,
    db: Session = Depends(get_db),
):
    db_album = db.query(Album).filter(Album.id == album_id).first()

    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # Ensures the associated artist exists.
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    db_album.title = album.title
    db_album.artist_id = album.artist_id

    # Saves the updated album to the database.
    db.commit()
    db.refresh(db_album)

    return db_album


# Deletes an existing album.
@router.delete("/{album_id}", status_code=204)
def delete_album(album_id: int, db: Session = Depends(get_db)):
    db_album = db.query(Album).filter(Album.id == album_id).first()

    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # Prevents deletion while the album has associated tracks.
    if db_album.tracks:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete an album that has associated tracks",
        )

    # Removes the album from the database.
    db.delete(db_album)
    db.commit()


# Retrieves all tracks belonging to an album.
@router.get("/{album_id}/tracks", response_model=list[TrackResponse])
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    db_album = db.query(Album).filter(Album.id == album_id).first()

    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    tracks = db.query(Track).filter(Track.album_id == album_id).all()
    return tracks
