import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.models import User, Role

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, db_session):
    # Ensure role 'client' exists (done automatically in route, but we check database state)
    response = await client.post(
        "/api/auth/register",
        json={"username": "new_user", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "new_user"

    # Verify user exists in database
    stmt = select(User).where(User.name == "new_user")
    user = (await db_session.execute(stmt)).scalar_one_or_none()
    assert user is not None
    assert user.name == "new_user"

@pytest.mark.asyncio
async def test_register_user_duplicate(client: AsyncClient):
    # First registration
    response1 = await client.post(
        "/api/auth/register",
        json={"username": "duplicate_user", "password": "password123"}
    )
    assert response1.status_code == 200

    # Second registration with same username
    response2 = await client.post(
        "/api/auth/register",
        json={"username": "duplicate_user", "password": "differentpassword"}
    )
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Это имя пользователя уже занято"

@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient):
    # Register first
    await client.post(
        "/api/auth/register",
        json={"username": "login_user", "password": "secretpassword"}
    )

    # Login with correct password
    response = await client.post(
        "/api/auth/login",
        json={"username": "login_user", "password": "secretpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "login_user"

@pytest.mark.asyncio
async def test_login_user_wrong_password(client: AsyncClient):
    # Register first
    await client.post(
        "/api/auth/register",
        json={"username": "login_wrong_pwd", "password": "secretpassword"}
    )

    # Login with wrong password
    response = await client.post(
        "/api/auth/login",
        json={"username": "login_wrong_pwd", "password": "wrongpassword"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"
