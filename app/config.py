from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    FastAPI best practice: Keep configuration strongly-typed and centralized.
    Pydantic automatically coerces types (e.g. str -> int, JSON string -> list).
    """

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Security & JWT
    SECRET_KEY: str = "showcase-secret-key-do-not-use-in-production-12345678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database connection URL (SQLite by default for zero-friction setup)
    DATABASE_URL: str = "sqlite://db.sqlite3"

    # CORS Allowed Origins
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
