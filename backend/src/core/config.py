from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent.parent.parent / ".env",
            Path(__file__).parent.parent.parent.parent / ".env"
        ],
        extra="ignore"
    )


settings = Settings()


class BaseSchema(BaseModel):
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    class Config:
        from_attributes = True
