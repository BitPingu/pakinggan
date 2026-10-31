from pydantic import BaseModel, ConfigDict


# validates data when creating an artist
class ArtistCreate(BaseModel):
    name: str 


# validates data when updating an artist
class ArtistUpdate(BaseModel):
    name: str


# defines the structure returned by the api
class ArtistResponse(BaseModel):
    id: int
    name: str

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)

