from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.config import BaseSchema
from src.core.database import db_dep
from src.models import MenuItem, FoodBasket, BasketItem
from src.schemas.basket_item import CreateBasketItemSchema, BasketItemSchema
from src.schemas.food_basket import FoodBasketSchema, ItemsFoodBasketSchema, FinalizeOrderSchema, UpdateOrderStatusSchema
from src.schemas.menu_item import CreateMenuItemSchema, MenuItemSchema
from src.core.dependencies import actual_user_id_dep, requires

router = APIRouter(prefix="/food_baskets", tags=["FoodBasket"])


@router.get("")
async def list_user_baskets(session: db_dep, user_id: actual_user_id_dep):
    food_stmt = select(FoodBasket).options(selectinload(FoodBasket.user)).where(FoodBasket.user_id == user_id)
    food_baskets = await session.scalars(food_stmt)
    return [FoodBasketSchema.model_validate(food_basket) for food_basket in food_baskets]


@router.get("/{food_basket_id}/basket_items")
async def list_food_basket_items(food_basket_id: int, session: db_dep, user_id: actual_user_id_dep):
    food_basket = await session.scalar(
        select(FoodBasket).options(
            selectinload(FoodBasket.basket_items).selectinload(BasketItem.menu_item)
        ).where(FoodBasket.id == food_basket_id)
    )
    if not food_basket or food_basket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    return [BasketItemSchema.model_validate(basket_item) for basket_item in food_basket.basket_items]


class IdMenuItemSchema(BaseSchema):
    menu_item_id: int


@router.post("", dependencies=[requires("orders:create")])
async def add_menu_item(menu_item_schema: IdMenuItemSchema, session: db_dep,
                        user_id: actual_user_id_dep) -> BasketItemSchema:
    menu_item = await session.get(MenuItem, menu_item_schema.menu_item_id)
    if not menu_item:
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


@router.post("/{basket_id}", dependencies=[requires("orders:create")])
async def order_basket(basket_id: int, order_data: FinalizeOrderSchema, session: db_dep, user_id: actual_user_id_dep):
    food_basket = await session.get(FoodBasket, basket_id)
    if not food_basket or food_basket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    if food_basket.is_ordered:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Заказ для этой корзины уже оформлен")
    if order_data.order_type == "delivery" and not order_data.address:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Необходимо указать адрес доставки")
        
    food_basket.mark_ordered(
        order_type=order_data.order_type,
        phone=order_data.phone,
        address=order_data.address
    )
    await session.commit()
    return {"detail": "FoodBasket ordered"}


@router.get("/orders", dependencies=[requires("orders:read")])
async def list_all_orders(session: db_dep):
    stmt = select(FoodBasket).options(
        selectinload(FoodBasket.basket_items).selectinload(BasketItem.menu_item),
        selectinload(FoodBasket.user)
    ).where(FoodBasket.is_ordered == True)
    orders = await session.scalars(stmt)
    return [ItemsFoodBasketSchema.model_validate(order) for order in orders]


@router.patch("/orders/{order_id}/status", dependencies=[requires("orders:write")])
async def update_order_status(order_id: int, status_data: UpdateOrderStatusSchema, session: db_dep):
    order = await session.get(FoodBasket, order_id)
    if not order or not order.is_ordered:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    
    order.status = status_data.status
    await session.commit()
    return {"detail": "Order status updated", "status": order.status}


@router.delete("/basket_items/{basket_item_id}")
async def remove_basket_item(basket_item_id: int, session: db_dep, user_id: actual_user_id_dep):
    stmt = select(BasketItem).options(selectinload(BasketItem.food_basket)).where(BasketItem.id == basket_item_id)
    basket_item = await session.scalar(stmt)
    if not basket_item or basket_item.food_basket.user_id != user_id or basket_item.food_basket.is_ordered:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Элемент корзины не найден")
        
    if basket_item.item_quantity > 1:
        basket_item.item_quantity -= 1
        await session.commit()
        return {"detail": "Quantity decreased", "item_quantity": basket_item.item_quantity}
    else:
        await session.delete(basket_item)
        await session.commit()
        return {"detail": "Basket item removed", "item_quantity": 0}
