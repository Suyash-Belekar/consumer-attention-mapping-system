from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
# Dynamically anchor project root directory so .env is always found reliably
BASE_DIR = Path(__file__).resolve().parent.parent.parent



class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Consumer Attention Mapping System"
    API_V1_STR: str = "/api/v1"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins value: {v}")

    # Database Configuration (Defaults aligned with docker-compose.yml)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "consumer_analytics"

    # Synchronous Database Connection String (psycopg2)
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # Asynchronous Database Connection String (asyncpg)
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # JWT & Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    AUTO_MIGRATE: bool = True
    DEV_AUTH_BYPASS: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()