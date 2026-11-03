from pydantic import BaseModel, ConfigDict


# validates data when creating a track
class TrackCreate(BaseModel):
    title: str
    duration: int | None = None
    album_id: int # foreign key


# validates data when updating a track
class TrackUpdate(BaseModel):
    title: str
    duration: int | None = None
    album_id: int


# defines the structure returned by the api
class TrackResponse(BaseModel):
    id: int
    title: str
    duration: int | None
    album_id: int

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)

