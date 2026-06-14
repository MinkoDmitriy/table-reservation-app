import asyncio
import datetime as dt
from typing import Annotated

import jwt
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from pydantic import Field

from src.core.config import BaseSchema, settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Header(BaseSchema):
    alg: str = settings.JWT_ALGORITHM
    typ: str = "JWT"


class FullPayload(BaseSchema):
    sub: Annotated[str | None, Field(default=None)]
    exp: Annotated[int | None, Field(default=None)]
    type: str = "access"
    scopes: list[str] = []


# Centralized mapping of roles to scopes
ROLE_SCOPES = {
    "client": ["client:base", "reservations:create", "orders:create"],
    "manager": ["tables:write", "menu:write", "reservations:read", "reservations:write", "orders:read", "orders:write"],
    "admin": ["admin:all", "users:write", "locations:write", "places:write"]
}


async def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = await asyncio.to_thread(bcrypt.gensalt)
    hashed = await asyncio.to_thread(bcrypt.hashpw, pwd_bytes, salt)
    return hashed.decode('utf-8')


async def verify_password(password: str, hashed_password: str) -> bool:
    pwd_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return await asyncio.to_thread(bcrypt.checkpw, pwd_bytes, hashed_bytes)


def create_access_token(sub: str, scopes: list[str] = None, expires_delta_minutes: int | None = None) -> str:
    if expires_delta_minutes is None:
        expires_delta_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=expires_delta_minutes)).timestamp()
    full_payload = FullPayload(sub=sub, exp=int(exp), type="access", scopes=scopes or [])
    
    access_token = jwt.encode(
        payload=full_payload.model_dump(),
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return access_token


def create_refresh_token(sub: str, expires_delta_days: int | None = None) -> str:
    if expires_delta_days is None:
        expires_delta_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # Refresh tokens do not require scopes
    exp = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=expires_delta_days)).timestamp()
    full_payload = FullPayload(sub=sub, exp=int(exp), type="refresh", scopes=[])
    
    refresh_token = jwt.encode(
        payload=full_payload.model_dump(),
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return refresh_token


def create_tokens(sub: str, scopes: list[str] = None) -> dict:
    access_token = create_access_token(sub, scopes=scopes)
    refresh_token = create_refresh_token(sub)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def decode_token(token: str) -> dict:
    decoded_token = jwt.decode(
        jwt=token,
        key=settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return decoded_token


def get_token_from_request(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        parts = auth_header.split()
        if len(parts) == 2:
            return parts[1]
    return None
