from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistResponse


# artist endpoints
router = APIRouter(
    prefix="/api/artists",
    tags=["Artists"],
)


# retrieve all artists
@router.get("/", response_model=list[ArtistResponse])
def get_artists(db: Session = Depends(get_db)):
    artists = db.query(Artist).all()
    return artists


# retrieve an individual artist
@router.get("/{artist_id}", response_model=ArtistResponse)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    # retrieve the artist
    artist = db.query(Artist).filter(Artist.id == artist_id).first()

    # handle missing artists
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # return the artist
    return artist


# create an artist
@router.post("/", response_model=ArtistResponse, status_code=201)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(name=artist.name) # creates a new artist object

    db.add(db_artist) # add it to the session
    db.commit() # commit the transaction
    db.refresh(db_artist) # refresh the object

    return db_artist # return in json


# update an existing artist
@router.put("/{artist_id}", response_model=ArtistResponse)
def update_artist(
    artist_id: int,
    artist: ArtistUpdate,
    db: Session = Depends(get_db),
):
    # retrieve the artist
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    # handle missing artists
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # update the field
    db_artist.name = artist.name

    # save the changes
    db.commit()
    db.refresh(db_artist)

    # return the updated artist
    return db_artist


# delete an artist
@router.delete("/{artist_id}", status_code=204)
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    # retrieve the artist
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()

    # handle missing artists
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # mark the artist for deletion
    db.delete(db_artist)

    # save the changes
    db.commit()

