from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# represents incoming registration data
# including the plaintext password
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()  # remove leading and trailing whitespace

        if not value:
            raise ValueError("Username cannot be empty")

        return value


# represents outgoing user data
# excluding the password and hash
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    # read from object attributes
    model_config = ConfigDict(from_attributes=True)
