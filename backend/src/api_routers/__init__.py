from fastapi import APIRouter

from src.api_routers import auth, user, reservation, food_table, food_place, location, food_basket, menu_item

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(user.router)

api_router.include_router(location.router)
api_router.include_router(food_place.router)
api_router.include_router(food_table.router)
api_router.include_router(reservation.router)
api_router.include_router(food_basket.router)
api_router.include_router(menu_item.router)


