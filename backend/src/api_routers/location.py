from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.core.database import db_dep
from src.models import Location
from src.schemas.location import LocationSchema, CreateLocationSchema
from src.core.dependencies import only_admin_dep, actual_user_id_dep

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("")
async def list_locations(session: db_dep, user_id: actual_user_id_dep):
    request = select(Location)
    response = await session.execute(request)
    locations = [LocationSchema.model_validate(location) for location in response.scalars().all()]
    return locations


@router.get("/{location_id}")
async def get_location(location_id: int, session: db_dep, user_id: actual_user_id_dep):
    location = await session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return LocationSchema.model_validate(location)


@router.post("")
async def create_location(location_schema: CreateLocationSchema, session: db_dep,
                          user_id: only_admin_dep):
    check_request = select(Location).where(Location.name == location_schema.name)
    if (await session.execute(check_request)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Location with this name already exists")
    location = Location(**location_schema.model_dump())
    session.add(location)
    await session.commit()
    await session.refresh(location)
    return LocationSchema.model_validate(location)


@router.put("/{location_id}")
async def update_location(location_id: int, location_schema: CreateLocationSchema, session: db_dep,
                          user_id: only_admin_dep):
    location = await session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    for attr, value in location_schema.model_dump().items():
        setattr(location, attr, value)
    await session.commit()
    await session.refresh(location)
    return LocationSchema.model_validate(location)


@router.delete("/{location_id}")
async def delete_location(location_id: int, session: db_dep, user_id: only_admin_dep):
    location = await session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    await session.delete(location)
    await session.commit()
    return {"detail": "Location deleted"}
