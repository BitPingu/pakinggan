from pydantic import BaseModel


# Represents the user's Last.fm connection status.
class LastFMStatus(BaseModel):
    connected: bool
    lastfm_username: str | None = None
