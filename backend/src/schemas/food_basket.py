import datetime as dt
from typing import Annotated
from pydantic import Field

from src.core.config import BaseSchema
from src.schemas.basket_item import BasketItemSchema


class FoodBasketSchema(BaseSchema):
    id: int
    food_place_id: int
    ordered_at: Annotated[dt.datetime | None, Field(default=None)]
    is_ordered: Annotated[bool | None, Field(default=False)]
    order_type: str | None = None
    phone: str | None = None
    address: str | None = None
    status: str = "new"
    user_name: str | None = None


class ItemsFoodBasketSchema(FoodBasketSchema):
    basket_items: list[BasketItemSchema]


class FinalizeOrderSchema(BaseSchema):
    order_type: str  # dinein, delivery
    phone: str
    address: str | None = None


class UpdateOrderStatusSchema(BaseSchema):
    status: str  # new, preparing, ready, completed, cancelled
