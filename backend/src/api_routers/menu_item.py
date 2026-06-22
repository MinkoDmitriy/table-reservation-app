from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import db_dep
from src.models import MenuItem, FoodPlace, BasketItem, FoodBasket
from src.schemas.menu_item import CreateMenuItemSchema, MenuItemSchema
from src.schemas.basket_item import CreateBasketItemSchema, BasketItemSchema
from src.core.dependencies import actual_user_id_dep, only_admin_dep, requires

router = APIRouter(prefix="/menu_items", tags=["MenuItem"])


_menu_cache = None


@router.get("")
async def list_menu_items(session: db_dep) -> list[MenuItemSchema]:
    global _menu_cache
    if _menu_cache is not None:
        return _menu_cache
    
    menu_items = await session.scalars(select(MenuItem).where(MenuItem.is_active == True))
    _menu_cache = [MenuItemSchema.model_validate(menu_item) for menu_item in menu_items]
    return _menu_cache


@router.get("/{item_id}")
async def get_menu_item(item_id: int, session: db_dep) -> MenuItemSchema:
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item or not menu_item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено")
    return MenuItemSchema.model_validate(menu_item)


@router.post("", dependencies=[requires("menu:write")])
async def create_menu_item(menu_item_schema: CreateMenuItemSchema, session: db_dep) -> MenuItemSchema:
    global _menu_cache
    place = await session.get(FoodPlace, menu_item_schema.food_place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден")
    menu_item = MenuItem(**menu_item_schema.model_dump())
    session.add(menu_item)
    await session.commit()
    await session.refresh(menu_item)
    _menu_cache = None  # Invalidate cache
    return MenuItemSchema.model_validate(menu_item)


@router.delete("/{item_id}", dependencies=[requires("menu:write")])
async def delete_menu_item(item_id: int, session: db_dep):
    global _menu_cache
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item or not menu_item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено")
    menu_item.is_active = False
    await session.commit()
    _menu_cache = None  # Invalidate cache
    return {"detail": "Блюдо успешно удалено"}


@router.post("/{item_id}/food_baskets")
async def add_menu_item_to_food_basket(item_id: int, session: db_dep, user_id: actual_user_id_dep) -> BasketItemSchema:
    menu_item = await session.get(MenuItem, item_id)
    if not menu_item or not menu_item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено")
    
    food_basket_stmt = select(FoodBasket).options(selectinload(FoodBasket.basket_items)).where(
        FoodBasket.user_id == user_id, FoodBasket.food_place_id == menu_item.food_place_id,
        FoodBasket.is_ordered == False)
    food_basket = await session.scalar(food_basket_stmt)
    if not food_basket:
        food_basket = FoodBasket(food_place_id=menu_item.food_place_id, user_id=user_id)
        session.add(food_basket)
        await session.flush()
        
    basket_item_stmt = select(BasketItem).where(
        BasketItem.food_basket_id == food_basket.id,
        BasketItem.menu_item_id == menu_item.id
    )
    basket_item = await session.scalar(basket_item_stmt)
    if basket_item:
        basket_item.item_quantity += 1
    else:
        basket_item = BasketItem(
            food_basket_id=food_basket.id,
            menu_item_id=menu_item.id,
            item_quantity=1
        )
        session.add(basket_item)
        
    await session.commit()
    
    stmt = select(BasketItem).options(selectinload(BasketItem.menu_item)).where(BasketItem.id == basket_item.id)
    basket_item = await session.scalar(stmt)
    return BasketItemSchema.model_validate(basket_item)
