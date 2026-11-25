from pydantic import BaseModel, Field


# Represents the user's Last.fm connection status.
class LastFMStatus(BaseModel):
    connected: bool
    lastfm_username: str | None = None


# Represents a recently played Last.fm track.
class LastFMTrack(BaseModel):
    name: str
    artist: str
    album: str | None = None
    url: str | None = None
    image: str | None = None
    played_at: str | None = None
    uts: str | None = Field(default=None, exclude=True)
    nowplaying: bool = False


# Represents the user's recent Last.fm tracks.
class LastFMRecentTracks(BaseModel):
    tracks: list[LastFMTrack]
