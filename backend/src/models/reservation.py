import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint, select, not_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import FoodTable, User


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("30 <= duration_in_minutes and duration_in_minutes <= 240", name="check_duration_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    start_datetime: Mapped[dt.datetime] = mapped_column(nullable=False)
    duration_in_minutes: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_table_id: Mapped[int] = mapped_column(ForeignKey("food_tables.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reservations")
    food_table: Mapped["FoodTable"] = relationship("FoodTable", back_populates="reservations")

    @property
    def user_name(self) -> str | None:
        return self.user.name if self.user else None

    @property
    def table_number(self) -> str | None:
        return self.food_table.table_number if self.food_table else None

    @property
    def max_seats(self) -> int | None:
        return self.food_table.max_seats if self.food_table else None

    @property
    def food_place_id(self) -> int | None:
        return self.food_table.food_place_id if self.food_table else None

    @property
    def end_datetime(self) -> dt.datetime:
        return self.start_datetime + dt.timedelta(minutes=self.duration_in_minutes)

    async def time_is_free(self, session: AsyncSession) -> bool:
        left = dt.datetime.combine(date=self.start_datetime.date(), time=dt.time(0, 0, 0))
        right = left + dt.timedelta(days=2)
        stmt = select(Reservation).where(
            Reservation.food_table_id == self.food_table_id,
            left <= Reservation.start_datetime,
            Reservation.start_datetime <= right
        )
        reservations = (await session.execute(stmt)).scalars()
        for reservation in reservations:
            if not (
                    self.start_datetime >= reservation.end_datetime or reservation.start_datetime >= self.end_datetime):
                return False
        return True

    async def time_is_free_sql(self, session: AsyncSession) -> bool:
        stmt = select(Reservation).where(
            Reservation.food_table_id == self.food_table_id,
            not_(
                or_(self.start_datetime >= Reservation.end_datetime, Reservation.start_datetime >= self.end_datetime),
            )
        )
        reservation = await session.execute(stmt)
        return reservation.scalar_one_or_none() is None

    async def reservation_in_working_time(self, session: AsyncSession) -> bool:
        from src.models import FoodTable
        stmt = select(FoodTable).options(selectinload(FoodTable.food_place)).where(FoodTable.id == self.food_table_id)
        food_table = (await session.execute(stmt)).scalar_one()
        food_place = food_table.food_place
        open_time = food_place.open_time
        close_time = food_place.close_time
        open_date = self.start_datetime.date()
        if close_time < open_time:
            close_date = open_date + dt.timedelta(days=1)
        else:
            close_date = open_date
        open_datetime = dt.datetime.combine(date=open_date, time=open_time)
        close_datetime = dt.datetime.combine(date=close_date, time=close_time)
        return open_datetime <= self.start_datetime and self.end_datetime <= close_datetime
