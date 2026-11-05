from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.schemas.album import AlbumCreate, AlbumUpdate, AlbumResponse
from app.schemas.track import TrackResponse


# album endpoints
router = APIRouter(
    prefix="/api/albums",
    tags=["Albums"],
)


# retrieve all albums
@router.get("/", response_model=list[AlbumResponse])
def get_albums(db: Session = Depends(get_db)):
    albums = db.query(Album).all()
    return albums


# retrieve a single album
@router.get("/{album_id}", response_model=AlbumResponse)
def get_album(album_id: int, db: Session = Depends(get_db)):
    # retrieve the album
    album = db.query(Album).filter(Album.id == album_id).first()

    # handle missing albums
    if album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # return the album
    return album


# create an album
@router.post("/", response_model=AlbumResponse, status_code=201)
def create_album(album: AlbumCreate, db: Session = Depends(get_db)):
    # check whether artist exists
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    # handle missing artists
    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # creates a new album object
    db_album = Album(
        title=album.title,
        artist_id=album.artist_id,
    )

    db.add(db_album) # add it to the session
    db.commit() # commit the transaction
    db.refresh(db_album) # refresh the object

    # return in json
    return db_album


# update an existing album
@router.put("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: int,
    album: AlbumUpdate,
    db: Session = Depends(get_db),
):
    # retrieve the album
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # handle missing albums
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # check whether artist exists
    db_artist = db.query(Artist).filter(Artist.id == album.artist_id).first()

    # handle missing artists
    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # update the fields
    db_album.title = album.title
    db_album.artist_id = album.artist_id

    # save the changes
    db.commit()
    db.refresh(db_album)

    # return the updated album
    return db_album


# delete an album
@router.delete("/{album_id}", status_code=204)
def delete_album(album_id: int, db: Session = Depends(get_db)):
    # retrieve the album
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # handle missing albums
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # mark the album for deletion
    db.delete(db_album)

    # save the changes
    db.commit()


# retrieve an album's tracks
@router.get("/{album_id}/tracks", response_model=list[TrackResponse])
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    # retrieve the album
    db_album = db.query(Album).filter(Album.id == album_id).first()

    # handle missing albums
    if db_album is None:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )

    # retrieve the album's tracks
    tracks = db.query(Track).filter(Track.album_id == album_id).all()

    # return the tracks
    return tracks

