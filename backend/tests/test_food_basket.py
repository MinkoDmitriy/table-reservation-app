import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_add_item_to_basket(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    item_id = seed_data["menu_item_id"]

    # Add item to basket
    response = await client.post(
        f"/api/menu_items/{item_id}/food_baskets",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["menu_item_id"] == item_id
    assert data["item_quantity"] == 1
    assert "food_basket_id" in data

@pytest.mark.asyncio
async def test_order_basket_missing_phone(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    item_id = seed_data["menu_item_id"]

    # 1. Add item to basket to create it
    basket_resp = await client.post(
        f"/api/menu_items/{item_id}/food_baskets",
        headers=headers
    )
    basket_id = basket_resp.json()["food_basket_id"]

    # 2. Checkout order with empty phone
    checkout_payload = {
        "order_type": "dinein",
        "phone": "",  # Empty phone
        "address": ""
    }
    response = await client.post(
        f"/api/food_baskets/{basket_id}",
        json=checkout_payload,
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Необходимо указать телефон"

@pytest.mark.asyncio
async def test_order_basket_delivery_missing_address(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    item_id = seed_data["menu_item_id"]

    # 1. Add item to basket
    basket_resp = await client.post(
        f"/api/menu_items/{item_id}/food_baskets",
        headers=headers
    )
    basket_id = basket_resp.json()["food_basket_id"]

    # 2. Checkout delivery order with empty address
    checkout_payload = {
        "order_type": "delivery",
        "phone": "+79998887766",
        "address": ""  # Empty address for delivery
    }
    response = await client.post(
        f"/api/food_baskets/{basket_id}",
        json=checkout_payload,
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Необходимо указать адрес доставки"

@pytest.mark.asyncio
async def test_order_basket_dinein_without_address_success(client: AsyncClient, authenticated_user: dict, seed_data: dict):
    headers = authenticated_user["headers"]
    item_id = seed_data["menu_item_id"]

    # 1. Add item to basket
    basket_resp = await client.post(
        f"/api/menu_items/{item_id}/food_baskets",
        headers=headers
    )
    basket_id = basket_resp.json()["food_basket_id"]

    # 2. Checkout dinein order without address (success scenario)
    checkout_payload = {
        "order_type": "dinein",
        "phone": "+79998887766",
        "address": ""  # Empty address is allowed for dinein
    }
    response = await client.post(
        f"/api/food_baskets/{basket_id}",
        json=checkout_payload,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "FoodBasket ordered"
