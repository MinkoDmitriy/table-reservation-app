from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.core.database import db_dep
from src.models import Reservation, FoodTable
from src.schemas.reservation import ReservationSchema, CreateReservationSchema, DTCreateReservationSchema
from src.core.dependencies import actual_user_id_dep, only_admin_dep

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("")
async def list_reservations(session: db_dep, user_id: actual_user_id_dep) -> list[ReservationSchema]:
    request = select(Reservation).where(Reservation.user_id == user_id)
    response = await session.execute(request)
    reservations = [ReservationSchema.model_validate(reservation) for reservation in response.scalars().all()]
    return reservations


@router.get('/all')
async def list_all_reservations(session: db_dep, user_id: only_admin_dep) -> list[ReservationSchema]:
    request = select(Reservation)
    response = await session.execute(request)
    reservations = [ReservationSchema.model_validate(reservation) for reservation in response.scalars().all()]
    return reservations


@router.get("/{reservation_id}")
async def get_reservation(reservation_id: int, session: db_dep, user_id: actual_user_id_dep) -> ReservationSchema:
    reservation = await session.get(Reservation, reservation_id)
    if reservation is None or reservation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return ReservationSchema.model_validate(reservation)


@router.post("")
async def create_reservation(reservation_schema: CreateReservationSchema, session: db_dep,
                             user_id: actual_user_id_dep) -> ReservationSchema:
    food_table = await session.get(FoodTable, reservation_schema.food_table_id)
    if food_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodTable with this id not found")
    reservation = Reservation(**reservation_schema.model_dump(), user_id=user_id)
    if not await reservation.time_is_free(session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This time slot is already occupied")
    if not await reservation.reservation_in_working_time(session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This time slot is outside of working time.")
    session.add(reservation)
    await session.commit()
    await session.refresh(reservation)
    return ReservationSchema.model_validate(reservation)


@router.post("/date_and_time")
async def create_reservation_date_and_time(dt_reservation_schema: DTCreateReservationSchema,
                                           session: db_dep,
                                           user_id: actual_user_id_dep) -> ReservationSchema:
    reservation_schema = CreateReservationSchema.convert_dt_schema(dt_reservation_schema)
    return await create_reservation(reservation_schema, session, user_id)


@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int, session: db_dep, user_id: actual_user_id_dep):
    reservation = await session.get(Reservation, reservation_id)
    if reservation is None or reservation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    await session.delete(reservation)
    await session.commit()
    return {"detail": "Reservation deleted"}
