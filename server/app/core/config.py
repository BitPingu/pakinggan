import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None  # optional

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Last.fm API configuration.
    LASTFM_API_KEY: str
    LASTFM_SHARED_SECRET: str
    LASTFM_ENCRYPTION_KEY: str

    # Frontend URL used for password-reset links and authentication redirects.
    FRONTEND_URL: str = "http://localhost:5173"

    # Backend URL used for external authentication callbacks.
    BACKEND_URL: str = "http://localhost:8000"

    # Email delivery configuration.
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "noreply@pakinggan.local"
    SMTP_USE_TLS: bool = False

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
