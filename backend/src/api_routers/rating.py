import datetime as dt

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func, or_

from src.core.database import db_dep
from src.models import Rating, FoodPlace, FoodBasket, Reservation, FoodTable
from src.schemas.rating import CreateRatingSchema, RatingSchema
from src.core.dependencies import actual_user_id_dep

router = APIRouter(prefix="/ratings", tags=["Rating"])


async def user_has_interaction_with_place(session, user_id: int, food_place_id: int) -> bool:
    basket_stmt = select(FoodBasket.id).where(
        FoodBasket.user_id == user_id,
        FoodBasket.food_place_id == food_place_id,
        FoodBasket.is_ordered == True
    )
    if (await session.scalar(basket_stmt)) is not None:
        return True

    res_stmt = select(Reservation.id).join(FoodTable).where(
        Reservation.user_id == user_id,
        FoodTable.food_place_id == food_place_id
    )
    if (await session.scalar(res_stmt)) is not None:
        return True

    return False


@router.post("")
async def create_or_toggle_rating(rating_data: CreateRatingSchema, session: db_dep,
                                   user_id: actual_user_id_dep):
    place = await session.get(FoodPlace, rating_data.food_place_id)
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден")

    if not await user_has_interaction_with_place(session, user_id, rating_data.food_place_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете оценить только те заведения, в которых заказывали или бронировали столик"
        )

    existing_stmt = select(Rating).where(
        Rating.user_id == user_id,
        Rating.food_place_id == rating_data.food_place_id
    )
    existing = await session.scalar(existing_stmt)

    if existing:
        if existing.score == rating_data.score:
            await session.delete(existing)
            await session.commit()
            return {"deleted": True, "score": 0, "food_place_id": rating_data.food_place_id}
        else:
            existing.score = rating_data.score
    else:
        rating = Rating(
            score=rating_data.score,
            user_id=user_id,
            food_place_id=rating_data.food_place_id
        )
        session.add(rating)

    await session.commit()

    result_stmt = select(Rating).where(
        Rating.user_id == user_id,
        Rating.food_place_id == rating_data.food_place_id
    )
    rating = await session.scalar(result_stmt)
    if rating:
        return RatingSchema.model_validate(rating)
    return {"deleted": True, "score": 0, "food_place_id": rating_data.food_place_id}


@router.get("/food_place/{food_place_id}")
async def get_food_place_ratings(food_place_id: int, session: db_dep):
    stmt = select(
        func.avg(Rating.score).label("avg_rating"),
        func.count(Rating.id).label("ratings_count")
    ).where(Rating.food_place_id == food_place_id)
    row = (await session.execute(stmt)).one()
    return {
        "avg_rating": round(float(row.avg_rating), 1) if row.avg_rating else None,
        "ratings_count": row.ratings_count
    }


@router.get("/user/history")
async def get_user_history(session: db_dep, user_id: actual_user_id_dep):
    basket_stmt = (
        select(FoodBasket)
        .where(FoodBasket.user_id == user_id, FoodBasket.is_ordered == True)
        .order_by(FoodBasket.ordered_at.desc())
    )
    baskets = (await session.scalars(basket_stmt)).all()

    res_stmt = (
        select(Reservation)
        .where(Reservation.user_id == user_id)
        .order_by(Reservation.start_datetime.desc())
    )
    reservations = (await session.scalars(res_stmt)).all()

    history = []

    for b in baskets:
        place_stmt = select(FoodPlace.name).where(FoodPlace.id == b.food_place_id)
        place_name = await session.scalar(place_stmt) or "Неизвестно"
        history.append({
            "id": b.id,
            "type": "order",
            "place_name": place_name,
            "food_place_id": b.food_place_id,
            "date": b.ordered_at.isoformat() if b.ordered_at else None,
            "status": b.status,
            "order_type": b.order_type,
            "phone": b.phone,
            "address": b.address,
        })

    for r in reservations:
        table_stmt = select(FoodTable).where(FoodTable.id == r.food_table_id)
        table = await session.scalar(table_stmt)
        place_name = "Неизвестно"
        place_id = None
        if table:
            pn_stmt = select(FoodPlace.name).where(FoodPlace.id == table.food_place_id)
            place_name = await session.scalar(pn_stmt) or "Неизвестно"
            place_id = table.food_place_id
        history.append({
            "id": r.id,
            "type": "reservation",
            "place_name": place_name,
            "food_place_id": place_id,
            "date": r.start_datetime.isoformat(),
            "status": "active",
            "table_number": r.table_number,
            "duration": r.duration_in_minutes,
        })

    history.sort(key=lambda x: x.get("date") or "", reverse=True)
    return history


@router.get("/user/{food_place_id}")
async def get_user_rating(food_place_id: int, session: db_dep, user_id: actual_user_id_dep):
    stmt = select(Rating).where(
        Rating.user_id == user_id,
        Rating.food_place_id == food_place_id
    )
    rating = await session.scalar(stmt)
    return RatingSchema.model_validate(rating) if rating else None


@router.get("/user/{food_place_id}/can_rate")
async def can_user_rate(food_place_id: int, session: db_dep, user_id: actual_user_id_dep):
    has = await user_has_interaction_with_place(session, user_id, food_place_id)
    return {"can_rate": has}
