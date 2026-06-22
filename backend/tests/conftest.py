import asyncio
import datetime as dt
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import app
from src.core.database import get_db
from src.models import Base, Location, FoodPlace, MenuItem, FoodTable, Role, User
from src.core import security

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = TestingSessionLocal(bind=connection)
        
        yield session
        
        await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture(autouse=True)
def override_db(db_session: AsyncSession):
    async def _get_test_db():
        yield db_session
        
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# Custom test fixtures for quick entity creations
@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession) -> Role:
    role = Role(name="client")
    db_session.add(role)
    await db_session.flush()
    return role

@pytest_asyncio.fixture
async def authenticated_user(client: AsyncClient, test_role) -> dict:
    """Helper to register and login a user. Returns dict with headers and user data."""
    username = "test_user_fixtures"
    password = "password123"
    
    reg_response = await client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    data = reg_response.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    
    return {
        "user_id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest_asyncio.fixture
async def authenticated_manager(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Helper to register a manager with manager permissions."""
    role = Role(name="manager")
    db_session.add(role)
    await db_session.flush()
    
    username = "test_manager_fixtures"
    password = "password123"
    
    hashed_password = await security.hash_password(password)
    user = User(hashed_password=hashed_password, name=username, role_id=role.id)
    db_session.add(user)
    await db_session.flush()
    
    scopes = security.ROLE_SCOPES.get("manager", [])
    token = security.create_access_token(str(user.id), scopes=scopes)
    await db_session.commit()
    
    return {
        "user_id": user.id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession) -> dict:
    """Seeds a single Location, FoodPlace, MenuItem, and FoodTable for tests."""
    location = Location(name="Тестовый Город")
    db_session.add(location)
    await db_session.flush()
    
    place = FoodPlace(
        name="Вкусный Ресторан",
        address="ул. Программистов, 42",
        description="Лучший ресторан в тестовом городе",
        open_time=dt.time(9, 0),
        close_time=dt.time(22, 0),
        location_id=location.id
    )
    db_session.add(place)
    await db_session.flush()
    
    item = MenuItem(
        name="Пицца Маргарита",
        price=550.00,
        description="Классическая пицца",
        food_place_id=place.id
    )
    db_session.add(item)
    
    table = FoodTable(
        table_number="1",
        max_seats=4,
        food_place_id=place.id
    )
    db_session.add(table)
    
    await db_session.commit()
    
    return {
        "location_id": location.id,
        "place_id": place.id,
        "menu_item_id": item.id,
        "table_id": table.id
    }
