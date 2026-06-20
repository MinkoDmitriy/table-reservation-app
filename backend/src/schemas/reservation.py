import datetime as dt
from typing import Annotated

from pydantic import Field, field_validator

from src.core.config import BaseSchema


class DTCreateReservationSchema(BaseSchema):
    date: dt.date
    start_time: dt.time
    duration_in_minutes: Annotated[int, Field(ge=30, le=240)]
    food_table_id: int

    @field_validator("start_time", mode="before")
    def parse_time(cls, v):
        if isinstance(v, str):
            try:
                return dt.datetime.strptime(v, "%H:%M").time()
            except ValueError:
                raise ValueError("Time should be of the form Hours:Minutes")
        return v


class CreateReservationSchema(BaseSchema):
    start_datetime: dt.datetime
    duration_in_minutes: Annotated[int, Field(ge=30, le=240)]
    food_table_id: int

    @classmethod
    def convert_dt_schema(cls, dt_reservation_schema: DTCreateReservationSchema):
        start_datetime = dt.datetime.combine(date=dt_reservation_schema.date,
                                             time=dt_reservation_schema.start_time)
        reservation_schema = CreateReservationSchema(
            **dt_reservation_schema.model_dump(exclude=("start_time", "date")), start_datetime=start_datetime)
        return reservation_schema

    @field_validator("start_datetime", mode="before")
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return dt.datetime.strptime(v, "%d.%m.%Y %H:%M")
            except ValueError:
                raise ValueError("Time should be of the form day.month.year-Hours:Minutes")
        return v


class ReservationSchema(CreateReservationSchema):
    id: int
    user_id: int
    end_datetime: dt.datetime
    user_name: str | None = None
    table_number: str | None = None
    max_seats: int | None = None
    food_place_id: int | None = None
