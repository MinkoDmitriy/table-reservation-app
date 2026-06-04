import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

while TYPE_CHECKING:
    from src.models import Location, FoodTable, FoodBasket, MenuItem


class FoodPlace(Base):
    __tablename__ = "food_places"
    __table_args__ = (
        UniqueConstraint("name", "location_id", "address", name="unique_name_per_location_id_and_address"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    open_time: Mapped[dt.time] = mapped_column(nullable=False)
    close_time: Mapped[dt.time] = mapped_column(nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    # Many To One
    location: Mapped["Location"] = relationship("Location", back_populates="food_places")
    # One To Many
    food_tables: Mapped[list["FoodTable"]] = relationship("FoodTable", back_populates="food_place")
    food_baskets: Mapped[list["FoodBasket"]] = relationship("FoodBasket", back_populates="food_place",
                                                       cascade="all, delete-orphan", passive_deletes=True)
    menu_items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="food_place",
                                                        cascade="all, delete-orphan", passive_deletes=True)
