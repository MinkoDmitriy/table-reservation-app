from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.core import security
from src.core.dependencies import db_dep
from src.models import User
from src.crud import user_crud
from src.schemas import auth

# Note: Keeping prefix="/auth" is necessary for AuthMiddleware matching and API structure
router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginSchema(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str


def create_tokens_with_user(user_id: int, user_name: str):
    """Create tokens and include user data in response."""
    access_token = security.create_access_token(str(user_id))
    refresh_token = security.create_refresh_token(str(user_id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": user_name
        }
    }


@router.post("/register")
async def register_user(auth_schema: auth.AuthSchema, session: db_dep):
    existing_user = await user_crud.schema_get_by_name(session, auth_schema.username)
    if existing_user is not None:
        raise HTTPException(detail="This name is already taken", status_code=status.HTTP_409_CONFLICT)

    hashed_password = await security.hash_password(auth_schema.password)
    user = User(hashed_password=hashed_password, name=auth_schema.username)
    await user_crud.create(session, user)
    await session.commit()
    return create_tokens_with_user(user.id, user.name)


@router.post("/login")
async def login_user(login_schema: LoginSchema, session: db_dep):
    user = await user_crud.get_by_name(session, login_schema.username)

    if not user or not await security.verify_password(login_schema.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this name and password not found")
    return create_tokens_with_user(user.id, user.name)


@router.post("/refresh")
async def refresh_access_token(refresh_schema: auth.RefreshTokenSchema):
    payload = security.decode_token(refresh_schema.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    new_access_token = security.create_access_token(sub=user_id)
    return {"access_token": new_access_token, "token_type": "bearer"}
