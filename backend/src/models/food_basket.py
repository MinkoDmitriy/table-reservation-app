import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
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

    order_type: Mapped[str | None] = mapped_column(default="dinein", nullable=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    address: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="new", nullable=False)

    # Relationships
    # Many To One
    user: Mapped["User"] = relationship("User", back_populates="food_baskets")

    @property
    def user_name(self) -> str | None:
        return self.user.name if self.user else None
    food_place: Mapped["FoodPlace"] = relationship("FoodPlace", back_populates="food_baskets")
    # One To Many
    basket_items: Mapped[list["BasketItem"]] = relationship("BasketItem",
                                                            cascade="all, delete-orphan",
                                                            passive_deletes=True, back_populates="food_basket")

    def mark_ordered(self, order_type: str, phone: str, address: str | None = None):
        self.ordered_at = dt.datetime.now()
        self.is_ordered = True
        self.order_type = order_type
        self.phone = phone
        self.address = address
        self.status = "new"
