from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, status, HTTPException, Request
import uuid
from typing import Annotated

from fastapi_limiter.depends import RateLimiter
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.postgres import get_session
from db.repository import UserRepository
from schemas.entity import (
    UserCreate, UserInDB, UserChangePassword, UserChangeLogin, LoginSchema,
    UserRoleAssign, UserRoleInDB, UserPermissionsInfo,
    PermissionCheckRequest, PermissionCheckResponse,
    RoleHierarchyCheck, RoleHierarchyResponse
)
from schemas.token import TokenResponse
from services.auth import AuthService
from services.role_service import RoleService
from models.entity import User, Role
from services.permission_service import PermissionService
from constants.permissions import RolePermissions, RolePriority
from core.config import settings

router = APIRouter(prefix="/users")
SessionDep = Annotated[AsyncSession, Depends(get_session)]

_signup_rate_deps = (
    [
        Depends(
            RateLimiter(
                times=settings.signup_rate_limit_times,
                seconds=settings.signup_rate_limit_seconds,
            )
        )
    ]
    if settings.rate_limit_enabled
    else []
)
_login_rate_deps = (
    [
        Depends(
            RateLimiter(
                times=settings.login_rate_limit_times,
                seconds=settings.login_rate_limit_seconds,
            )
        )
    ]
    if settings.rate_limit_enabled
    else []
)


@router.post('/signup', status_code=status.HTTP_201_CREATED, dependencies=_signup_rate_deps)
async def create_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)):
    """Регистрация пользователя."""
    user_repo = UserRepository(session)

    existing_user = await user_repo.get_user_by_login(user_create.login)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )

    existing_email = await user_repo.get_user_by_email(user_create.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await user_repo.create_user(
        login=user_create.login,
        email=user_create.email,
        password=user_create.password,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role_name=user_create.role_name
    )

    user_with_roles = await user_repo.get_user_by_id(user.id)
    if not user_with_roles:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user"
        )
    
    user_roles = await user_repo.get_user_role_names(user.id)

    response = {
        "id": str(user_with_roles.id),
        "login": user_with_roles.login,
        "email": user_with_roles.email,
        "first_name": user_with_roles.first_name,
        "last_name": user_with_roles.last_name,
        "roles": user_roles,
        "primary_role": user_roles[0] if user_roles else "user"
    }
    
    return response


@router.post("/login", response_model=TokenResponse, dependencies=_login_rate_deps)
async def login(payload: LoginSchema, request: Request, session: AsyncSession = Depends(get_session), Authorize: AuthJWT = Depends()):
    """Аутентификация."""
    auth_service = AuthService(session, Authorize)
    tokens = await auth_service.login(request, payload.login, payload.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
        session: AsyncSession = Depends(get_session),
        Authorize: AuthJWT = Depends()
):
    """Обновление access токена"""
    auth_service = AuthService(session, Authorize)
    return await auth_service.refresh_tokens()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(session: AsyncSession = Depends(get_session), Authorize: AuthJWT = Depends()):
    """Сброс токенов."""
    auth_service = AuthService(session, Authorize)
    await auth_service.logout()


@router.post("/change-login")
async def change_login(
    payload: UserChangeLogin,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Смена логина."""
    auth_service = AuthService(session, Authorize)
    await auth_service.change_login(payload.new_login)
    return {"msg": "Login updated"}


@router.post("/change-password")
async def change_password(
    payload: UserChangePassword,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Смена пароля."""
    auth_service = AuthService(session, Authorize)
    await auth_service.change_password(payload.current_password, payload.new_password)
    return {"msg": "Password updated"}


@router.get("/login-history")
async def login_history(
    limit: int = 50,
    offset: int = 0,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """Получение пользователем своей истории входов в аккаунт."""
    auth_service = AuthService(session, Authorize)
    return await auth_service.login_history(limit, offset)


@router.post("/roles/assign", response_model=UserRoleInDB, status_code=status.HTTP_201_CREATED)
async def assign_role(
    role_assign: UserRoleAssign, 
    session: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Assign role to user"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])
    
    role_service = RoleService(session)
    try:
        role = await role_service.assign_role_to_user(
            user_id=role_assign.user_id,
            role_name=role_assign.role_name,
            assigner_user_id=current_user_id
        )
        # Load role_type for response
        await session.refresh(role, ["role_type"])
        return role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/roles/remove/{user_id}/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role(
    user_id: uuid.UUID,
    role_name: str,
    session: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Remove role from user"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])
    
    role_service = RoleService(session)
    try:
        await role_service.remove_role_from_user(
            user_id=user_id,
            role_name=role_name,
            remover_user_id=current_user_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/permissions/{user_id}", response_model=UserPermissionsInfo)
async def get_user_permissions(
    user_id: uuid.UUID,
    session: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Get detailed permission information for user"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])
    
    permission_service = PermissionService(session)
    
    # Check if user can view permissions
    if not await permission_service.check_permission(current_user_id, RolePermissions.VIEW_PERMISSIONS):
        # Only allow users to view their own permissions
        if current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' permissions"
            )
    
    return await permission_service.get_user_permissions_details(user_id)


@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(
    request: PermissionCheckRequest,
    session: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Check if user has specific permission"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])
    
    permission_service = PermissionService(session)
    
    # Map permission names to bit masks
    permission_map = {
        "create_roles": RolePermissions.CREATE_ROLES,
        "edit_roles": RolePermissions.EDIT_ROLES,
        "assign_roles": RolePermissions.ASSIGN_ROLES,
        "delete_roles": RolePermissions.DELETE_ROLES,
        "view_permissions": RolePermissions.VIEW_PERMISSIONS,
        "manage_permissions": RolePermissions.MANAGE_PERMISSIONS
    }
    
    if request.permission not in permission_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown permission: {request.permission}"
        )
    
    required_permission = permission_map[request.permission]
    has_permission = await permission_service.check_permission(request.user_id, required_permission)
    
    user_permissions = await permission_service.get_user_permissions_details(request.user_id)
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        user_permissions=user_permissions["permissions"]
    )


@router.post("/hierarchy/check", response_model=RoleHierarchyResponse)
async def check_role_hierarchy(
    request: RoleHierarchyCheck,
    session: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Check if user can assign specific role"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])
    
    permission_service = PermissionService(session)
    
    can_assign = await permission_service.can_assign_role_to_user(
        assigner_user_id=request.assigner_user_id,
        target_role_name=request.target_role_name
    )
    
    reason = None
    if not can_assign:
        user_repo = UserRepository(session)
        assigner_priority = await user_repo.get_highest_role_priority(request.assigner_user_id)
        target_role = await permission_service.role_type_repo.get_role_by_name(request.target_role_name.lower())
        
        if not target_role:
            reason = f"Role '{request.target_role_name}' does not exist"
        elif not await permission_service.check_permission(request.assigner_user_id, RolePermissions.ASSIGN_ROLES):
            reason = "User does not have permission to assign roles"
        elif not RolePriority.can_assign_role(assigner_priority, target_role.priority):
            reason = f"Cannot assign role with priority {target_role.priority} (user priority: {assigner_priority})"
    
    return RoleHierarchyResponse(
        can_assign=can_assign,
        reason=reason
    )


# Legacy role management endpoints (updated to work with new structure)
@router.get("/roles", response_model=list[UserRoleInDB])
async def get_user_roles(
    db: SessionDep,
    Authorize: AuthJWT = Depends()
) -> list[UserRoleInDB]:
    """Get all user roles (admin only)"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    
    # Check if user can manage roles using new permission service
    permission_service = PermissionService(db)
    current_user_id = uuid.UUID(claims["user_id"])
    
    if not await permission_service.check_permission(current_user_id, RolePermissions.MANAGE_PERMISSIONS):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    query = select(Role).options(selectinload(Role.role_type))
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/roles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_roles(
    user_id: uuid.UUID, 
    db: SessionDep,
    Authorize: AuthJWT = Depends()
):
    """Clear all roles from user (admin only)"""
    await Authorize.jwt_required()
    claims = await Authorize.get_raw_jwt()
    
    # Check if user can manage roles using new permission service
    permission_service = PermissionService(db)
    current_user_id = uuid.UUID(claims["user_id"])
    
    if not await permission_service.check_permission(current_user_id, RolePermissions.MANAGE_PERMISSIONS):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    user_repo = UserRepository(db)
    await user_repo.role_repo.clear_user_roles(user_id)
    return