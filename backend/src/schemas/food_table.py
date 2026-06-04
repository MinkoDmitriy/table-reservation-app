from src.core.config import BaseSchema


class CreateFoodTableSchema(BaseSchema):
    table_number: str
    max_seats: int
    food_place_id: int


class UpdateFoodTableSchema(BaseSchema):
    table_number: str | None
    max_seats: int | None


class FoodTableSchema(CreateFoodTableSchema):
    id: int
