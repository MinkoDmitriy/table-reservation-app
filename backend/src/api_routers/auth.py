from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core import security
from src.core.dependencies import db_dep
from src.models import User, Role
from src.crud.user_crud import user_crud
from src.schemas import auth

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginSchema(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str


def create_tokens_with_user(user: User, role_name: str):
    """Create tokens and include user data and scopes in response."""
    scopes = security.ROLE_SCOPES.get(role_name, [])
    access_token = security.create_access_token(str(user.id), scopes=scopes)
    refresh_token = security.create_refresh_token(str(user.id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.name
        }
    }


@router.post("/register")
async def register_user(auth_schema: auth.AuthSchema, session: db_dep):
    # Ensure default 'client' role exists in database
    role_stmt = select(Role).where(Role.name == "client")
    role = (await session.execute(role_stmt)).scalar_one_or_none()
    if not role:
        role = Role(name="client")
        session.add(role)
        await session.flush()

    user_stmt = select(User).where(User.name == auth_schema.username)
    existing_user = (await session.execute(user_stmt)).scalar_one_or_none()
    if existing_user is not None:
        raise HTTPException(detail="Это имя пользователя уже занято", status_code=status.HTTP_409_CONFLICT)

    hashed_password = await security.hash_password(auth_schema.password)
    user = User(hashed_password=hashed_password, name=auth_schema.username, role_id=role.id)
    await user_crud.create(session, user)
    await session.commit()
    return create_tokens_with_user(user, role.name)


@router.post("/login")
async def login_user(login_schema: LoginSchema, session: db_dep):
    # Eagerly load the user role to fetch its name
    query = select(User).where(User.name == login_schema.username).options(selectinload(User.role))
    user = (await session.execute(query)).scalar_one_or_none()

    if not user or not await security.verify_password(login_schema.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неверное имя пользователя или пароль")
    
    role_name = user.role.name if user.role else "client"
    return create_tokens_with_user(user, role_name)


@router.post("/refresh")
async def refresh_access_token(refresh_schema: auth.RefreshTokenSchema, session: db_dep):
    payload = security.decode_token(refresh_schema.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный тип токена")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректная сигнатура или данные токена")

    # Fetch user with role loaded
    query = select(User).where(User.id == int(user_id)).options(selectinload(User.role))
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    role_name = user.role.name if user.role else "client"
    scopes = security.ROLE_SCOPES.get(role_name, [])
    new_access_token = security.create_access_token(sub=user_id, scopes=scopes)
    return {"access_token": new_access_token, "token_type": "bearer"}
