from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.config import BaseSchema
from src.core.database import db_dep
from src.models import MenuItem, FoodBasket, BasketItem
from src.schemas.basket_item import CreateBasketItemSchema, BasketItemSchema
from src.schemas.food_basket import FoodBasketSchema, ItemsFoodBasketSchema
from src.schemas.menu_item import CreateMenuItemSchema, MenuItemSchema
from src.core.dependencies import actual_user_id_dep

router = APIRouter(prefix="/food_baskets", tags=["FoodBasket"])


@router.get("")
async def list_user_baskets(session: db_dep, user_id: actual_user_id_dep):
    food_stmt = select(FoodBasket).where(FoodBasket.user_id == user_id)
    food_baskets = await session.scalars(food_stmt)
    return [FoodBasketSchema.model_validate(food_basket) for food_basket in food_baskets]


@router.get("/{food_basket_id}/basket_items")
async def list_food_basket_items(food_basket_id: int, session: db_dep, user_id: actual_user_id_dep):
    food_basket = await session.scalar(
        select(FoodBasket).options(selectinload(FoodBasket.basket_items)).where(FoodBasket.id == food_basket_id))
    if not food_basket or food_basket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodBasket not found")
    return [BasketItemSchema.model_validate(basket_item) for basket_item in food_basket.basket_items]


class IdMenuItemSchema(BaseSchema):
    menu_item_id: int


@router.post("")
async def add_menu_item(menu_item_schema: IdMenuItemSchema, session: db_dep,
                        user_id: actual_user_id_dep) -> BasketItemSchema:
    menu_item = await session.get(MenuItem, menu_item_schema.menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    menu_item_schema = MenuItemSchema.model_validate(menu_item)
    food_basket_stmt = select(FoodBasket).options(selectinload(FoodBasket.basket_items)).where(
        FoodBasket.user_id == user_id, FoodBasket.food_place_id == menu_item_schema.food_place_id,
        FoodBasket.is_ordered == False)
    food_basket = await session.scalar(food_basket_stmt)
    if not food_basket:
        food_basket = FoodBasket(food_place_id=menu_item_schema.food_place_id, user_id=user_id)
        await session.add(food_basket)
        await session.refresh(food_basket)
    basket_item_schema = CreateBasketItemSchema(food_basket_id=food_basket.id,
                                                menu_item_id=menu_item_schema.id)
    basket_item = BasketItem(**basket_item_schema.model_dump())
    session.add(basket_item)
    session.commit()
    session.refresh(basket_item)
    return BasketItemSchema.model_validate(basket_item)


@router.post("/{basket_id}")
async def order_basket(basket_id: int, session: db_dep, user_id: actual_user_id_dep):
    food_basket = await session.get(FoodBasket, basket_id)
    if not food_basket or food_basket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodBasket not found")
    if food_basket.is_ordered:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="FoodBasket already ordered")
    food_basket.mark_ordered()
    await session.commit()
    return {"detail": "FoodBasket ordered"}
