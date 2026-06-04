from fastapi import APIRouter
from sqlalchemy import select

from src.core.database import db_dep
from src.models import User
from src.schemas.user import UserSchema, AdminSchema
from src.core.dependencies import actual_user_id_dep, only_admin_dep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_users(session: db_dep, user_id: only_admin_dep):
    request = select(User)
    users = (await session.execute(request)).scalars()
    return [AdminSchema.model_validate(user) for user in users]


@router.get("/me")
async def actual_user(session: db_dep, user_id: actual_user_id_dep):
    user = await session.get(User, user_id)
    return UserSchema.model_validate(user)
