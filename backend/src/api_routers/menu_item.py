from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import db_dep
from src.models import MenuItem, FoodPlace, BasketItem, FoodBasket
from src.schemas.menu_item import CreateMenuItemSchema, MenuItemSchema
from src.schemas.basket_item import CreateBasketItemSchema, BasketItemSchema
from src.core.dependencies import actual_user_id_dep, only_admin_dep

router = APIRouter(prefix="/menu_items", tags=["MenuItem"])


@router.get("")
async def list_menu_items(session: db_dep, user_id: actual_user_id_dep) -> list[MenuItemSchema]:
    menu_items = await session.scalars(select(MenuItem))
    return [MenuItemSchema.model_validate(menu_item) for menu_item in menu_items]


@router.get("/{item_id}")
async def get_menu_item(item_id: int, session: db_dep, user_id: actual_user_id_dep) -> MenuItemSchema:
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return MenuItemSchema.model_validate(menu_item)


@router.post("")
async def create_menu_item(menu_item_schema: CreateMenuItemSchema, session: db_dep,
                           user_id: only_admin_dep) -> MenuItemSchema:
    place = await session.get(FoodPlace, menu_item_schema.food_place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food place not found")
    menu_item = MenuItem(**menu_item_schema.model_dump())
    session.add(menu_item)
    await session.commit()
    await session.refresh(menu_item)
    return MenuItemSchema.model_validate(menu_item)


@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, session: db_dep, user_id: only_admin_dep):
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    session.delete(menu_item)
    await session.commit()
    return {"detail": "Menu item deleted"}


@router.post("/{item_id}/food_baskets")
async def add_menu_item_to_food_basket(item_id: int, session: db_dep, user_id: actual_user_id_dep) -> BasketItemSchema:
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    menu_item_schema = MenuItemSchema.model_validate(menu_item)
    food_basket_stmt = select(FoodBasket).options(selectinload(FoodBasket.basket_items)).where(
        FoodBasket.user_id == user_id, FoodBasket.food_place_id == menu_item_schema.food_place_id,
        FoodBasket.is_ordered == False)
    food_basket = await session.scalar(food_basket_stmt)
    if not food_basket:
        food_basket = FoodBasket(food_place_id=menu_item_schema.food_place_id, user_id=user_id)
        session.add(food_basket)
        await session.flush()
    basket_item_schema = CreateBasketItemSchema(food_basket_id=food_basket.id,
                                                menu_item_id=menu_item_schema.id)
    basket_item = BasketItem(**basket_item_schema.model_dump())
    session.add(basket_item)
    await session.commit()
    await session.refresh(basket_item)
    return BasketItemSchema.model_validate(basket_item)
