from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.schemas.album import AlbumResponse
from app.schemas.artist import ArtistCreate, ArtistResponse, ArtistUpdate

# Defines the API endpoints for managing artists.
router = APIRouter(
    prefix="/api/artists",
    tags=["Artists"],
)


# Retrieves all artists.
@router.get("/", response_model=list[ArtistResponse])
def get_artists(db: Session = Depends(get_db)):
    artists = db.query(Artist).all()
    return artists


# Retrieves a single artist by ID.
@router.get("/{artist_id}", response_model=ArtistResponse)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    return artist


# Creates a new artist.
@router.post("/", response_model=ArtistResponse, status_code=201)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(name=artist.name)

    # Saves the new artist to the database.
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)

    return db_artist


# Updates an existing artist.
@router.put("/{artist_id}", response_model=ArtistResponse)
def update_artist(
    artist_id: int,
    artist: ArtistUpdate,
    db: Session = Depends(get_db),
):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    db_artist.name = artist.name

    # Saves the updated artist to the database.
    db.commit()
    db.refresh(db_artist)

    return db_artist


# Deletes an existing artist.
@router.delete("/{artist_id}", status_code=204)
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    # Prevents deletion while the artist has associated albums.
    if db_artist.albums:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete an artist that has associated albums",
        )

    # Removes the artist from the database.
    db.delete(db_artist)
    db.commit()


# Retrieves all albums belonging to an artist.
@router.get("/{artist_id}/albums", response_model=list[AlbumResponse])
def get_artist_albums(artist_id: int, db: Session = Depends(get_db)):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    if db_artist is None:
        raise HTTPException(
            status_code=404,
            detail="Artist not found",
        )

    albums = db.query(Album).filter(Album.artist_id == artist_id).all()
    return albums
