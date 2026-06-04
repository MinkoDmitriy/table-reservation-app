from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

while TYPE_CHECKING:
    from src.models import FoodPlace, BasketItem


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("name", "food_place_id", name="unique_name_with_food_place_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    food_place_id: Mapped[int] = mapped_column(ForeignKey("food_places.id", ondelete="CASCADE"), nullable=False)

    food_place: Mapped["FoodPlace"] = relationship("FoodPlace", back_populates="menu_items")
    basket_items: Mapped[list["BasketItem"]] = relationship("BasketItem", back_populates="menu_item",
                                                            passive_deletes=True, cascade="all, delete-orphan")
