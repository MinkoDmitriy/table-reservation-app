from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

while TYPE_CHECKING:
    from src.models import FoodPlace


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    food_places: Mapped[list["FoodPlace"]] = relationship("FoodPlace", back_populates="location")




