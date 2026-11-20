from pydantic import BaseModel, ConfigDict, Field, field_validator


# Validates data when creating a track.
class TrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    duration: int | None = Field(default=None, ge=0)
    album_id: int = Field(gt=0)

    # Removes surrounding whitespace and ensures the title is not empty.
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Track title cannot be empty")

        return value


# Validates data when updating a track.
class TrackUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    duration: int | None = Field(default=None, ge=0)
    album_id: int = Field(gt=0)

    # Removes surrounding whitespace and ensures the title is not empty.
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Track title cannot be empty")

        return value


# Defines the structure returned by the API.
class TrackResponse(BaseModel):
    id: int
    title: str
    duration: int | None
    album_id: int

    # Allows the schema to read data from ORM model attributes.
    model_config = ConfigDict(from_attributes=True)
