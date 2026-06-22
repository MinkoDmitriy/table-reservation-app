import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_reservation_success(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    table_id = seed_data["table_id"]

    # Book table at 19:00 for 120 minutes
    payload = {
        "start_datetime": "25.06.2026 19:00",
        "duration_in_minutes": 120,
        "food_table_id": table_id
    }
    response = await client.post(
        "/api/reservations",
        json=payload,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["food_table_id"] == table_id
    assert data["duration_in_minutes"] == 120

@pytest.mark.asyncio
async def test_reservation_collision_overbooking(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    table_id = seed_data["table_id"]

    # 1. Create first booking at 19:00
    payload = {
        "start_datetime": "25.06.2026 19:00",
        "duration_in_minutes": 120,
        "food_table_id": table_id
    }
    resp1 = await client.post(
        "/api/reservations",
        json=payload,
        headers=headers
    )
    assert resp1.status_code == 200

    # 2. Try to book the same table at 19:00 from another user (or same, but on same time slot)
    # Register another user to be realistic
    user2_resp = await client.post(
        "/api/auth/register",
        json={"username": "user_two", "password": "password123"}
    )
    token2 = user2_resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp2 = await client.post(
        "/api/reservations",
        json=payload,
        headers=headers2
    )
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Этот временной интервал уже забронирован"

@pytest.mark.asyncio
async def test_manager_change_order_status_success(client: AsyncClient, authenticated_user: dict, authenticated_manager: dict, seed_data: dict):
    # 1. User registers, adds item to basket, and checkouts order
    user_headers = authenticated_user["headers"]
    item_id = seed_data["menu_item_id"]

    basket_resp = await client.post(
        f"/api/menu_items/{item_id}/food_baskets",
        headers=user_headers
    )
    basket_id = basket_resp.json()["food_basket_id"]

    checkout_payload = {
        "order_type": "dinein",
        "phone": "+79998887766",
        "address": ""
    }
    await client.post(
        f"/api/food_baskets/{basket_id}",
        json=checkout_payload,
        headers=user_headers
    )

    # 2. Ordinary client tries to change order status to preparing (Should fail: 403)
    client_patch_resp = await client.patch(
        f"/api/food_baskets/orders/{basket_id}/status",
        json={"status": "preparing"},
        headers=user_headers
    )
    assert client_patch_resp.status_code == 403
    assert "Недостаточно прав" in client_patch_resp.json()["detail"]

    # 3. Manager tries to change order status (Should succeed: 200)
    manager_headers = authenticated_manager["headers"]
    manager_patch_resp = await client.patch(
        f"/api/food_baskets/orders/{basket_id}/status",
        json={"status": "preparing"},
        headers=manager_headers
    )
    assert manager_patch_resp.status_code == 200
    assert manager_patch_resp.json()["detail"] == "Order status updated"
    assert manager_patch_resp.json()["status"] == "preparing"
