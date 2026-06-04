from pydantic import Field

from src.core.config import BaseSchema


class AuthSchema(BaseSchema):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=64)


class RefreshTokenSchema(BaseSchema):
    refresh_token: str
