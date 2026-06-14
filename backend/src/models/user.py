from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Reservation, FoodBasket, Role, Rating, FoodPlace

restaurant_managers = Table(
    "restaurant_managers",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("food_place_id", Integer, ForeignKey("food_places.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role: Mapped["Role"] = relationship("Role")

    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="user")
    food_baskets: Mapped[list["FoodBasket"]] = relationship("FoodBasket", back_populates="user")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")
    managed_places: Mapped[list["FoodPlace"]] = relationship(
        "FoodPlace", secondary=restaurant_managers, back_populates="managers"
    )
