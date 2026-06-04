import datetime as dt

from pydantic import field_validator

from src.core.config import BaseSchema


class UpdateFoodPlaceSchema(BaseSchema):
    name: str
    address: str
    description: str
    location_id: int


class CreateFoodPlaceSchema(UpdateFoodPlaceSchema):
    open_time: dt.time
    close_time: dt.time

    @field_validator("open_time", "close_time", mode="before")
    def parse_time(cls, v):
        if isinstance(v, str):
            try:
                return dt.datetime.strptime(v, "%H:%M").time()
            except ValueError:
                raise ValueError("Time should be of the form Hours:minutes")
        return v


class FoodPlaceSchema(CreateFoodPlaceSchema):
    id: int
