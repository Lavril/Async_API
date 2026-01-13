import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User, Role
from schemas.entity import UserCreate, UserInDB, RoleCreate, RoleInDB, RoleUpdate


router = APIRouter(prefix="/users")
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: SessionDep) -> UserInDB:
    existing_user_by_login = await db.execute(
        select(User).where(User.login == user_create.login)
    )
    if existing_user_by_login.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот логин уже занят"
        )

    existing_user_by_email = await db.execute(
        select(User).where(User.email == user_create.email)
    )
    if existing_user_by_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот почтовый адрес уже занят"
        )

    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/roles", response_model=RoleInDB, status_code=status.HTTP_201_CREATED)
async def set_roles(role_create: RoleCreate, db: SessionDep) -> RoleInDB:
    user_id = role_create.user_id

    user = await db.execute(select(User.id).where(User.id == user_id))
    if not user.scalar_one_or_none():
        raise HTTPException(404, "Пользователь не найден")

    result = await db.execute(select(Role).where(Role.user_id == user_id))
    if result.scalar_one_or_none():
        raise HTTPException(409, "У пользователя уже есть роль")

    role_dto = jsonable_encoder(role_create)
    role = Role(**role_dto)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.get("/roles", response_model=list[RoleInDB])
async def get_roles(db: SessionDep) -> list[RoleInDB]:
    query = select(Role)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/roles/{user_id}", response_model=RoleInDB, status_code=status.HTTP_200_OK)
async def update_roles(user_id: uuid.UUID, role_update: RoleUpdate, db: SessionDep) -> RoleInDB:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    result = await db.execute(select(Role).where(Role.user_id == user_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(404, "Роль не найдена")

    role.role = role_update.role

    await db.commit()
    await db.refresh(role)
    return role


@router.delete("/roles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roles(user_id: uuid.UUID, db: SessionDep):
    user = await db.execute(select(User.id).where(User.id == user_id))
    if not user.scalar_one_or_none():
        raise HTTPException(404, "Пользователь не найден")

    result = await db.execute(select(Role).where(Role.user_id == user_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "У пользователя нет роли")

    await db.execute(delete(Role).where(Role.user_id == user_id))
    await db.commit()

    return
