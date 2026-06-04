from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.core.database import db_dep
from src.models import FoodTable, FoodPlace
from src.schemas.food_table import FoodTableSchema, CreateFoodTableSchema, UpdateFoodTableSchema
from src.core.dependencies import only_authenticated_dep

router = APIRouter(prefix="/food_tables", tags=["FoodTables"])


@router.get("")
async def list_food_tables(session: db_dep):
    request = select(FoodTable)
    response = await session.execute(request)
    food_tables = [FoodTableSchema.model_validate(food_table) for food_table in response.scalars().all()]
    return food_tables


@router.get("/{food_table_id}")
async def get_food_table(food_table_id: int, session: db_dep):
    food_table = await session.get(FoodTable, food_table_id)
    if food_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FoodTableSchema.model_validate(food_table)


@router.post("")
async def create_food_table(food_table_schema: CreateFoodTableSchema, session: db_dep,
                            is_authenticated: only_authenticated_dep):
    food_place = await session.get(FoodPlace, food_table_schema.food_place_id)
    if food_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodPlace with this id not found")
    check_request = select(FoodTable).where(
        FoodTable.table_number == food_table_schema.table_number, FoodTable.food_place_id == food_table_schema.food_place_id)
    if (await session.execute(check_request)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="FoodTable with this name and food_place_id already exists")
    food_table = FoodTable(**food_table_schema.model_dump())
    session.add(food_table)
    await session.commit()
    await session.refresh(food_table)
    return FoodTableSchema.model_validate(food_table)


@router.put("/{food_table_id}")
async def update_food_table(food_table_id: int, food_table_schema: UpdateFoodTableSchema, session: db_dep,
                            is_authenticated: only_authenticated_dep):
    food_table = await session.get(FoodTable, food_table_id)
    if food_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodTable not found")
    check_request = select(FoodTable).where(
        FoodTable.table_number == food_table_schema.table_number, FoodTable.food_place_id == food_table.food_place_id)
    if (await session.execute(check_request)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="FoodTable with this name and food_place_id already exists")
    for attr, value in food_table_schema.model_dump().items():
        setattr(food_table, attr, value)
    await session.commit()
    await session.refresh(food_table)
    return FoodTableSchema.model_validate(food_table)


@router.delete("/{food_table_id}")
async def delete_food_table(food_table_id: int, session: db_dep, is_authenticated: only_authenticated_dep):
    food_table = await session.get(FoodTable, food_table_id)
    if food_table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodTable not found")
    await session.delete(food_table)
    await session.commit()
    return {"detail": "FoodTable deleted"}
