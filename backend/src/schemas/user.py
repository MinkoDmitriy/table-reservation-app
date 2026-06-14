from pydantic import Field

from src.core.config import BaseSchema


class CreateUserSchema(BaseSchema):
    name: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=64)
    role_name: str = Field(default="client", max_length=32)


class UpdateUserSchema(BaseSchema):
    name: str | None = Field(default=None, max_length=64)
    password: str | None = Field(default=None, max_length=64)
    role_name: str | None = Field(default=None, max_length=32)
    is_active: bool | None = None


class UpdateProfileSchema(BaseSchema):
    name: str | None = Field(default=None, min_length=3, max_length=64)
    phone: str | None = Field(default=None, max_length=32)


class UserSchema(BaseSchema):
    id: int
    name: str
    phone: str | None = None


class RoleResponseSchema(BaseSchema):
    id: int
    name: str


class AdminUserSchema(UserSchema):
    role: RoleResponseSchema | None = None
    managed_place_ids: list[int] = []


class ChangeRoleSchema(BaseSchema):
    role_name: str = Field(min_length=3, max_length=32)


class AssignManagerSchema(BaseSchema):
    food_place_ids: list[int]
