from functools import lru_cache
from logging import DEBUG, WARNING, INFO

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    PROJECT_TITLE: str = "Notes Manager"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_URL: str = ""
    PROJECT_LEVEL: str = "debug"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    DATABASE_URL: str

    JWT_ALGORITHM: str = "HS256"
    JWT_KEY: str
    ACCESS_TOKEN_EXPIRY_IN_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRY_IN_MINUTES: int = 7 * 24 * 60

    REDIS_URL: str
    GLOBAL_MAX_REQUESTS: int = 100
    GLOBAL_REFILL_TIME_IN_SECONDS: int = 60

    LOG_FILENAME: str = "app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024
    LOG_BACKUP_CNT: int = 5
    LOG_LEVEL: int = WARNING if PROJECT_LEVEL == "prod" else INFO


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
