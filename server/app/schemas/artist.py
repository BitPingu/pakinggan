from pydantic import BaseModel, ConfigDict, Field, field_validator


# validates data when creating an artist
class ArtistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip() # remove leading and trailing whitespace

        if not value:
            raise ValueError("Artist name cannot be empty")

        return value


# validates data when updating an artist
class ArtistUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip() # remove leading and trailing whitespace

        if not value:
            raise ValueError("Artist name cannot be empty")

        return value


# defines the structure returned by the api
class ArtistResponse(BaseModel):
    id: int
    name: str

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)

