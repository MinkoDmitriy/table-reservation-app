from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

engine = create_async_engine(settings.db_url)

session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with session_factory() as session:
        yield session


class Base(DeclarativeBase):
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


db_dep = Annotated[AsyncSession, Depends(get_db)]
