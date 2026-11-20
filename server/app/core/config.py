from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None  # optional

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Frontend URL used when generating password-reset links.
    FRONTEND_URL: str = "http://localhost:5173"

    # Email delivery configuration.
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "noreply@pakinggan.local"
    SMTP_USE_TLS: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
