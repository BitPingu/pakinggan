from pydantic import BaseModel, ConfigDict, Field, field_validator


# validates data when creating an album
class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: int = Field(gt=0) # foreign key

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip() # remove leading and trailing whitespace

        if not value:
            raise ValueError("Album title cannot be empty")

        return value


# validates data when updating an album
class AlbumUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip() # remove leading and trailing whitespace

        if not value:
            raise ValueError("Album title cannot be empty")

        return value


# defines the structure returned by the api
class AlbumResponse(BaseModel):
    id: int
    title: str
    artist_id: int

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)

