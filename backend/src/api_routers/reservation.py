import datetime as dt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import db_dep
from src.models import Reservation, FoodTable
from src.schemas.reservation import ReservationSchema, CreateReservationSchema, DTCreateReservationSchema
from src.core.dependencies import actual_user_id_dep, only_admin_dep, requires

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/occupied")
async def list_occupied_tables(
    food_place_id: int,
    date: dt.date,
    start_time: dt.time,
    session: db_dep,
    duration_in_minutes: int = 120
) -> list[int]:
    start_datetime = dt.datetime.combine(date, start_time)
    end_datetime = start_datetime + dt.timedelta(minutes=duration_in_minutes)
    
    day_start = dt.datetime.combine(date, dt.time(0, 0, 0))
    day_end = day_start + dt.timedelta(days=1)
    
    stmt = select(Reservation).join(FoodTable).where(
        FoodTable.food_place_id == food_place_id,
        Reservation.start_datetime >= day_start,
        Reservation.start_datetime < day_end
    )
    res_list = (await session.execute(stmt)).scalars().all()
    
    occupied_table_ids = []
    for res in res_list:
        res_end = res.start_datetime + dt.timedelta(minutes=res.duration_in_minutes)
        if not (start_datetime >= res_end or res.start_datetime >= end_datetime):
            occupied_table_ids.append(res.food_table_id)
            
    return list(set(occupied_table_ids))


@router.get("")
async def list_reservations(session: db_dep, user_id: actual_user_id_dep) -> list[ReservationSchema]:
    request = select(Reservation).options(
        selectinload(Reservation.user),
        selectinload(Reservation.food_table)
    ).where(Reservation.user_id == user_id)
    response = await session.execute(request)
    reservations = [ReservationSchema.model_validate(reservation) for reservation in response.scalars().all()]
    return reservations


@router.get('/all', dependencies=[requires("orders:read")])
async def list_all_reservations(session: db_dep) -> list[ReservationSchema]:
    request = select(Reservation).options(
        selectinload(Reservation.user),
        selectinload(Reservation.food_table)
    )
    response = await session.execute(request)
    reservations = [ReservationSchema.model_validate(reservation) for reservation in response.scalars().all()]
    return reservations


@router.get("/{reservation_id}")
async def get_reservation(reservation_id: int, session: db_dep, user_id: actual_user_id_dep) -> ReservationSchema:
    reservation = await session.scalar(
        select(Reservation).options(
            selectinload(Reservation.user),
            selectinload(Reservation.food_table)
        ).where(Reservation.id == reservation_id)
    )
    if reservation is None or reservation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return ReservationSchema.model_validate(reservation)


@router.post("", dependencies=[requires("reservations:create")])
async def create_reservation(reservation_schema: CreateReservationSchema, session: db_dep,
                             user_id: actual_user_id_dep) -> ReservationSchema:
    food_table = await session.get(FoodTable, reservation_schema.food_table_id)
    if food_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Столик с этим ID не найден")
    reservation = Reservation(**reservation_schema.model_dump(), user_id=user_id)
    if not await reservation.time_is_free(session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Этот временной интервал уже забронирован")
    if not await reservation.reservation_in_working_time(session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Выбранное время выходит за рамки часов работы ресторана")
    session.add(reservation)
    await session.commit()
    reservation = await session.scalar(
        select(Reservation).options(
            selectinload(Reservation.user),
            selectinload(Reservation.food_table)
        ).where(Reservation.id == reservation.id)
    )
    return ReservationSchema.model_validate(reservation)


@router.post("/date_and_time", dependencies=[requires("reservations:create")])
async def create_reservation_date_and_time(dt_reservation_schema: DTCreateReservationSchema,
                                           session: db_dep,
                                           user_id: actual_user_id_dep) -> ReservationSchema:
    reservation_schema = CreateReservationSchema.convert_dt_schema(dt_reservation_schema)
    return await create_reservation(reservation_schema, session, user_id)


@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int, session: db_dep, user_id: actual_user_id_dep):
    reservation = await session.get(Reservation, reservation_id)
    if reservation is None or reservation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")
    await session.delete(reservation)
    await session.commit()
    return {"detail": "Бронирование успешно отменено"}
