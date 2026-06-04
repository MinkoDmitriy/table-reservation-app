from pydantic import Field

from src.core.config import BaseSchema


class CreateUserSchema(BaseSchema):
    name: str = Field(max_length=128)


class UserSchema(CreateUserSchema):
    id: int


class AdminSchema(UserSchema):
    is_admin: bool
