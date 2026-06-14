from pydantic import Field

from src.core.config import BaseSchema


class CreateRatingSchema(BaseSchema):
    score: int = Field(ge=1, le=5)
    food_place_id: int


class RatingSchema(CreateRatingSchema):
    id: int
    user_id: int


class FoodPlaceRatingStatsSchema(BaseSchema):
    avg_rating: float | None = None
    ratings_count: int = 0
