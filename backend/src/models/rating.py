from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import User, FoodPlace


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint("1 <= score AND score <= 5", name="check_score_range"),
        UniqueConstraint("user_id", "food_place_id", name="unique_user_food_place_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_place_id: Mapped[int] = mapped_column(ForeignKey("food_places.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    food_place: Mapped["FoodPlace"] = relationship("FoodPlace", back_populates="ratings")
