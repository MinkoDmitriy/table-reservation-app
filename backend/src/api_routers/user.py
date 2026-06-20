from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import db_dep
from src.core import security
from src.models import User, Role, FoodPlace
from src.schemas.user import (
    UserSchema, AdminUserSchema, RoleResponseSchema,
    ChangeRoleSchema, CreateUserSchema, UpdateUserSchema,
    UpdateProfileSchema, AssignManagerSchema,
)
from src.core.dependencies import actual_user_id_dep, requires

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", dependencies=[requires("admin:all")])
async def list_users(session: db_dep):
    request = select(User).options(selectinload(User.role), selectinload(User.managed_places))
    users = (await session.execute(request)).scalars().all()
    result = []
    for user in users:
        schema = AdminUserSchema(
            id=user.id,
            name=user.name,
            role=RoleResponseSchema(id=user.role.id, name=user.role.name) if user.role else None,
            managed_place_ids=[mp.id for mp in user.managed_places]
        )
        result.append(schema)
    return result


@router.get("/me")
async def actual_user(session: db_dep, user_id: actual_user_id_dep):
    from sqlalchemy.orm import selectinload
    stmt = select(User).options(selectinload(User.managed_places)).where(User.id == user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "managed_place_ids": [mp.id for mp in user.managed_places]
    }


@router.put("/me")
async def update_my_profile(session: db_dep, user_id: actual_user_id_dep, schema: UpdateProfileSchema):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if schema.name is not None:
        existing = await session.scalar(select(User).where(User.name == schema.name, User.id != user_id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")
        user.name = schema.name

    if schema.phone is not None:
        user.phone = schema.phone

    await session.commit()
    await session.refresh(user)
    return {"message": "Профиль обновлён", "name": user.name, "phone": user.phone}


@router.get("/managers", dependencies=[requires("admin:all")])
async def list_managers(session: db_dep):
    stmt = select(User).options(selectinload(User.role), selectinload(User.managed_places)).join(Role).where(Role.name == "manager")
    managers = (await session.execute(stmt)).scalars().all()
    result = []
    for m in managers:
        result.append({
            "id": m.id,
            "name": m.name,
            "managed_place_ids": [mp.id for mp in m.managed_places]
        })
    return result


@router.post("", dependencies=[requires("admin:all")])
async def create_user(schema: CreateUserSchema, session: db_dep):
    role_stmt = select(Role).where(Role.name == schema.role_name)
    role = (await session.execute(role_stmt)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Роль '{schema.role_name}' не существует. Доступные роли: client, manager, admin.")

    existing = await session.scalar(select(User).where(User.name == schema.name))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")

    hashed = await security.hash_password(schema.password)
    user = User(name=schema.name, hashed_password=hashed, role_id=role.id)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"id": user.id, "name": user.name, "role": role.name}


@router.put("/{target_user_id}", dependencies=[requires("admin:all")])
async def update_user(target_user_id: int, schema: UpdateUserSchema, session: db_dep):
    user = await session.get(User, target_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if schema.name is not None:
        existing = await session.scalar(select(User).where(User.name == schema.name, User.id != target_user_id))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")
        user.name = schema.name

    if schema.password is not None:
        user.hashed_password = await security.hash_password(schema.password)

    if schema.role_name is not None:
        role_stmt = select(Role).where(Role.name == schema.role_name)
        role = (await session.execute(role_stmt)).scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Роль '{schema.role_name}' не существует. Доступные роли: client, manager, admin.")
        user.role_id = role.id

    if schema.is_active is not None:
        user.is_active = schema.is_active

    await session.commit()
    return {"message": "Пользователь обновлён"}


@router.delete("/{target_user_id}", dependencies=[requires("admin:all")])
async def delete_user(target_user_id: int, session: db_dep):
    user = await session.get(User, target_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    await session.delete(user)
    await session.commit()
    return {"detail": "Пользователь удалён"}


@router.put("/{target_user_id}/role", dependencies=[requires("admin:all")])
async def change_user_role(target_user_id: int, schema: ChangeRoleSchema, session: db_dep):
    user = await session.get(User, target_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    role_stmt = select(Role).where(Role.name == schema.role_name)
    role = (await session.execute(role_stmt)).scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Роль '{schema.role_name}' не существует. Доступные роли: client, manager, admin."
        )

    user.role_id = role.id
    await session.commit()
    return {"message": f"Роль пользователя '{user.name}' успешно изменена на '{role.name}'."}


@router.put("/{target_user_id}/managed_places", dependencies=[requires("admin:all")])
async def assign_managed_places(target_user_id: int, schema: AssignManagerSchema, session: db_dep):
    stmt = select(User).options(selectinload(User.managed_places)).where(User.id == target_user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    role = await session.get(Role, user.role_id)
    if not role or role.name != "manager":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Назначать рестораны можно только менеджерам")

    places = []
    for place_id in schema.food_place_ids:
        place = await session.get(FoodPlace, place_id)
        if not place:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ресторан с ID {place_id} не найден")
        places.append(place)

    user.managed_places = places
    await session.commit()
    return {"message": f"Рестораны назначены менеджеру '{user.name}'", "managed_place_ids": [p.id for p in places]}
