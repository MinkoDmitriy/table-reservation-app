from src.crud.base import SchemaCRUD
from src.models import User
from src.schemas.user import CreateUserSchema, UserSchema


class UserCRUD(SchemaCRUD[User, CreateUserSchema, UserSchema]):
    pass


user_crud = UserCRUD(User, CreateUserSchema, UserSchema)
