"""Зависимости FastAPI: сессия БД, репозитории и сервисы."""

from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.repository import UserRepository
from services.auth import AuthService
from services.permission_service import PermissionService
from services.role_service import RoleService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


AuthJWTDep = Annotated[AuthJWT, Depends()]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_service(session: SessionDep, auth_jwt: AuthJWTDep) -> AuthService:
    return AuthService(session, auth_jwt)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_role_service(session: SessionDep) -> RoleService:
    return RoleService(session)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]


def get_permission_service(session: SessionDep) -> PermissionService:
    return PermissionService(session)


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]


class PaginationParams:
    def __init__(
        self,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        self.limit = limit
        self.offset = offset

PaginationParamsDep = Annotated[PaginationParams, Depends()]