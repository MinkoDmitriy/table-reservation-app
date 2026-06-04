import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

while TYPE_CHECKING:
    from src.models import FoodPlace, BasketItem, User


class FoodBasket(Base):
    __tablename__ = "food_baskets"
    __table_args__ = (
        Index("user_id_is_ordered_index", "user_id", "is_ordered"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ordered_at: Mapped[dt.datetime | None] = mapped_column(default=None, nullable=True)
    is_ordered: Mapped[bool] = mapped_column(default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_place_id: Mapped[int] = mapped_column(ForeignKey("food_places.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    # Many To One
    user: Mapped["User"] = relationship("User", back_populates="food_baskets")
    food_place: Mapped["FoodPlace"] = relationship("FoodPlace", back_populates="food_baskets")
    # One To Many
    basket_items: Mapped[list["BasketItem"]] = relationship("BasketItem",
                                                            cascade="all, delete-orphan",
                                                            passive_deletes=True, back_populates="food_basket")

    def mark_ordered(self):
        self.ordered_at = dt.datetime.now()
        self.is_ordered = True
