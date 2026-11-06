from pydantic import BaseModel, ConfigDict, Field, field_validator


# validates data when creating a track
class TrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    duration: int | None = Field(default=None, ge=0)
    album_id: int = Field(gt=0)  # foreign key

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()  # remove leading and trailing whitespace

        if not value:
            raise ValueError("Track title cannot be empty")

        return value


# validates data when updating a track
class TrackUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    duration: int | None = Field(default=None, ge=0)
    album_id: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()  # remove leading and trailing whitespace

        if not value:
            raise ValueError("Track title cannot be empty")

        return value


# defines the structure returned by the api
class TrackResponse(BaseModel):
    id: int
    title: str
    duration: int | None
    album_id: int

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)
