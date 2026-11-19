from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.schemas.album import AlbumCreate, AlbumResponse, AlbumUpdate
from app.schemas.track import TrackResponse

# Define the album API endpoints.
router = APIRouter(
    prefix="/api/albums",
    tags=["Albums"],
)


# Retrieve all albums.
@router.get("/", response_model=list[AlbumResponse])
def get_albums(db: Session = Depends(get_db)):
    albums = db.query(Album).all()
    return albums


# Retrieve a single album by ID.
@router.get("/{album_id}", response_model=AlbumResponse)
def get_album(album_id: int, db: Session = Depends(get_db)):
    # Find the requested album.
    album = db.query(Album).filter(Album.id == album_id).first()

    # Return a 404 error if the album does not exist.
    if album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    return album


# Create a new album.
@router.post("/", response_model=AlbumResponse, status_code=201)
def create_album(album: AlbumCreate, db: Session = Depends(get_db)):
    # Verify that the associated artist exists.
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    # Return a 404 error if the artist does not exist.
    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # Create an album associated with the specified artist.
    db_album = Album(
        title=album.title,
        artist_id=album.artist_id,
    )

    # Save the new album to the database.
    db.add(db_album)
    db.commit()
    db.refresh(db_album)

    return db_album


# Update an existing album.
@router.put("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: int,
    album: AlbumUpdate,
    db: Session = Depends(get_db),
):
    # Find the album to update.
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # Return a 404 error if the album does not exist.
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # Verify that the new associated artist exists.
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    # Return a 404 error if the artist does not exist.
    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # Update the album's title and associated artist.
    db_album.title = album.title
    db_album.artist_id = album.artist_id

    # Save the updated album to the database.
    db.commit()
    db.refresh(db_album)

    return db_album


# Delete an existing album.
@router.delete("/{album_id}", status_code=204)
def delete_album(album_id: int, db: Session = Depends(get_db)):
    # Find the album to delete.
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # Return a 404 error if the album does not exist.
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # Delete the album from the database.
    db.delete(db_album)
    db.commit()


# Retrieve all tracks belonging to an album.
@router.get("/{album_id}/tracks", response_model=list[TrackResponse])
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    # Find the requested album.
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # Return a 404 error if the album does not exist.
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # Retrieve the tracks associated with the album.
    tracks = db.query(Track).filter(Track.album_id == album_id).all()

    return tracks
