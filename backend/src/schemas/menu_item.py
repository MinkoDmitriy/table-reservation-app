from typing import Annotated
from pydantic import Field
from decimal import Decimal

from src.core.config import BaseSchema


class CreateMenuItemSchema(BaseSchema):
    name: str
    description: Annotated[str | None, Field(default=None)]
    food_place_id: int
    price: Annotated[Decimal, Field(gt=0, decimal_places=2)]


class MenuItemSchema(CreateMenuItemSchema):
    id: int
