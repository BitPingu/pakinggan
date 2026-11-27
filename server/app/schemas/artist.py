from pydantic import BaseModel, ConfigDict, Field, field_validator


# Validates data when creating an artist.
class ArtistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    # Removes surrounding whitespace and ensures the name is not empty.
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Artist name cannot be empty")

        return value


# Validates data when updating an artist.
class ArtistUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    # Removes surrounding whitespace and ensures the name is not empty.
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Artist name cannot be empty")

        return value


# Defines the structure returned by the API.
class ArtistResponse(BaseModel):
    id: int
    name: str
    biography: str | None = None
    image_url: str | None = None
    genres: list[str] = Field(default_factory=list)

    # Converts Genre model objects into genre names.
    @field_validator("genres", mode="before")
    @classmethod
    def serialize_genres(cls, value) -> list[str]:
        return [
            genre.name if hasattr(genre, "name") else genre for genre in (value or [])
        ]

    # Allows the schema to read data from ORM model attributes.
    model_config = ConfigDict(from_attributes=True)
