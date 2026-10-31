from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import ArtistCreate, ArtistResponse


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


# create an artist
@router.post("/", response_model=ArtistResponse, status_code=201)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(name=artist.name) # creates a new artist object

    db.add(db_artist) # add it to the session
    db.commit() # commit the transaction
    db.refresh(db_artist) # refresh the object

    return db_artist # return in json

