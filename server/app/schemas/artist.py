from pydantic import BaseModel, ConfigDict


# defines an artist
class ArtistCreate(BaseModel):
    name: str 


# defines what the api returns
class ArtistResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

