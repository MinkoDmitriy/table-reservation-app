from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import FoodPlace, Reservation


class FoodTable(Base):
    __tablename__ = "food_tables"
    __table_args__ = (
        UniqueConstraint("table_number", "food_place_id", name="unique_table_number_per_food_place_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    table_number: Mapped[str] = mapped_column(nullable=False)
    max_seats: Mapped[int] = mapped_column(nullable=False)
    food_place_id: Mapped[int] = mapped_column(ForeignKey("food_places.id", ondelete="CASCADE"), nullable=False)

    food_place: Mapped["FoodPlace"] = relationship("FoodPlace", back_populates="food_tables")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="food_table")

