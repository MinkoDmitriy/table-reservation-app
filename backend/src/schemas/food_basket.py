import datetime as dt
from typing import Annotated
from pydantic import Field

from src.core.config import BaseSchema
from src.schemas.basket_item import BasketItemSchema


class FoodBasketSchema(BaseSchema):
    id: int
    ordered_at: Annotated[dt.datetime | None, Field(default=None)]
    is_ordered: Annotated[bool | None, Field(default=False)]


class ItemsFoodBasketSchema(FoodBasketSchema):
    items: list[BasketItemSchema]
