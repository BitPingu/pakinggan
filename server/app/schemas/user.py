from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Validates incoming registration data, including the plaintext password.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    # Removes surrounding whitespace and ensures the username is not empty.
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Username cannot be empty")

        return value


# Defines the user data returned by the API, excluding password information.
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    # Allows the schema to read data from SQLAlchemy model attributes.
    model_config = ConfigDict(from_attributes=True)


# Validates the username and password submitted during login.
class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    # Removes surrounding whitespace from the username.
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return value.strip()


# Defines the response returned after successful authentication.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Validates the email submitted when requesting a password reset.
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Validates the token and new password submitted during a password reset.
class PasswordResetRequest(BaseModel):
    token: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=128)


# Defines the generic response returned by password recovery endpoints.
class PasswordResetResponse(BaseModel):
    message: str
