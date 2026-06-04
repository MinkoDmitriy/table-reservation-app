from src.core.config import BaseSchema
from src.schemas.menu_item import MenuItemSchema


class CreateBasketItemSchema(BaseSchema):
    menu_item_id: int
    food_basket_id: int


class BasketItemSchema(CreateBasketItemSchema):
    id: int


class ItemSchema():
    menu_item: MenuItemSchema

