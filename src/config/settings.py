from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost"
    REDIS_DEFAULT_TIMEOUT: int = 60 * 30 # 30 min
    REDIS_PREFIX: str = "mslu-ical"

    class Config:
        env_file = ".env"

settings = Settings()
