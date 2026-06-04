from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

while TYPE_CHECKING:
    from src.models import MenuItem, FoodBasket


class BasketItem(Base):
    __tablename__ = "basket_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    food_basket_id: Mapped[int] = mapped_column(ForeignKey("food_baskets.id", ondelete="CASCADE"), nullable=False,
                                                index=True)

    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="basket_items")
    food_basket: Mapped["FoodBasket"] = relationship("FoodBasket", back_populates="basket_items")
