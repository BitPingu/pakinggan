from pydantic import BaseModel, ConfigDict


# validates data when creating an album
class AlbumCreate(BaseModel):
    title: str
    artist_id: int # foreign key


# validates data when updating an album
class AlbumUpdate(BaseModel):
    title: str
    artist_id: int


# defines the structure returned by the api
class AlbumResponse(BaseModel):
    id: int
    title: str
    artist_id: int

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)

