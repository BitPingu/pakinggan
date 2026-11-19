from pydantic import BaseModel, ConfigDict, Field, field_validator


# Validates data when creating an album.
class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: int = Field(gt=0)

    # Remove surrounding whitespace and reject empty titles.
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Album title cannot be empty")

        return value


# Validates data when updating an existing album.
class AlbumUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: int = Field(gt=0)

    # Remove surrounding whitespace and reject empty titles.
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Album title cannot be empty")

        return value


# Defines the album data returned by the API.
class AlbumResponse(BaseModel):
    id: int
    title: str
    artist_id: int

    # Allow the schema to read data from SQLAlchemy model attributes.
    model_config = ConfigDict(from_attributes=True)
