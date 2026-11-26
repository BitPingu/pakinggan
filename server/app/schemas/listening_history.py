from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Defines the artist information returned with a track.
class ListeningHistoryArtist(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# Defines the album information returned with a track.
class ListeningHistoryAlbum(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


# Defines the track information returned with a listening-history entry.
class ListeningHistoryTrack(BaseModel):
    id: int
    title: str
    duration: int | None
    artist: ListeningHistoryArtist
    album: ListeningHistoryAlbum | None

    model_config = ConfigDict(from_attributes=True)


# Defines a listening-history entry returned by the API.
class ListeningHistoryResponse(BaseModel):
    id: int
    played_at: datetime
    track: ListeningHistoryTrack

    model_config = ConfigDict(from_attributes=True)
