from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Reservation, FoodBasket


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="user")
    food_baskets: Mapped[list["FoodBasket"]] = relationship("FoodBasket", back_populates="user")
