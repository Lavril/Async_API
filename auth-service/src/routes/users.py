from fastapi import APIRouter, Depends, status, HTTPException, Request
import uuid

from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.config import settings
from dependencies import (
    AuthJWTDep,
    AuthServiceDep,
    PermissionServiceDep,
    RoleServiceDep,
    SessionDep,
    UserRepoDep,
)
from models.entity import User, Role
from schemas.entity import (
    UserCreate,
    UserChangePassword,
    UserChangeLogin,
    LoginSchema,
    UserRoleAssign,
    UserRoleInDB,
    UserPermissionsInfo,
    PermissionCheckRequest,
    PermissionCheckResponse,
    RoleHierarchyCheck,
    RoleHierarchyResponse,
)
from schemas.token import TokenResponse
from constants.permissions import RolePermissions, RolePriority

router = APIRouter(prefix="/users")

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


@router.post("/signup", status_code=status.HTTP_201_CREATED, dependencies=_signup_rate_deps)
async def create_user(user_create: UserCreate, user_repo: UserRepoDep):
    """Регистрация пользователя."""
    existing_user = await user_repo.get_user_by_login(user_create.login)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered",
        )

    existing_email = await user_repo.get_user_by_email(user_create.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await user_repo.create_user(
        login=user_create.login,
        email=user_create.email,
        password=user_create.password,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role_name=user_create.role_name,
    )

    user_with_roles = await user_repo.get_user_by_id(user.id)
    if not user_with_roles:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user",
        )

    user_roles = await user_repo.get_user_role_names(user.id)

    return {
        "id": str(user_with_roles.id),
        "login": user_with_roles.login,
        "email": user_with_roles.email,
        "first_name": user_with_roles.first_name,
        "last_name": user_with_roles.last_name,
        "roles": user_roles,
        "primary_role": user_roles[0] if user_roles else "user",
    }


@router.post("/login", response_model=TokenResponse, dependencies=_login_rate_deps)
async def login(
    payload: LoginSchema,
    request: Request,
    auth_service: AuthServiceDep,
):
    """Аутентификация."""
    return await auth_service.login(request, payload.login, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(auth_service: AuthServiceDep):
    """Обновление access токена"""
    print("refresh")
    return await auth_service.refresh_tokens()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(auth_service: AuthServiceDep):
    """Сброс токенов."""
    await auth_service.logout()


@router.post("/change-login")
async def change_login(payload: UserChangeLogin, auth_service: AuthServiceDep):
    """Смена логина."""
    await auth_service.change_login(payload.new_login)
    return {"msg": "Login updated"}


@router.post("/change-password")
async def change_password(payload: UserChangePassword, auth_service: AuthServiceDep):
    """Смена пароля."""
    await auth_service.change_password(payload.current_password, payload.new_password)
    return {"msg": "Password updated"}


@router.get("/login-history")
async def login_history(
    auth_service: AuthServiceDep,
    limit: int = 50,
    offset: int = 0,
):
    """Получение пользователем своей истории входов в аккаунт."""
    return await auth_service.login_history(limit, offset)


@router.post("/roles/assign", response_model=UserRoleInDB, status_code=status.HTTP_201_CREATED)
async def assign_role(
    role_assign: UserRoleAssign,
    session: SessionDep,
    jwt_auth: AuthJWTDep,
    role_service: RoleServiceDep,
):
    """Assign role to user"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    try:
        role = await role_service.assign_role_to_user(
            user_id=role_assign.user_id,
            role_name=role_assign.role_name,
            assigner_user_id=current_user_id,
        )
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
    jwt_auth: AuthJWTDep,
    role_service: RoleServiceDep,
):
    """Remove role from user"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    try:
        await role_service.remove_role_from_user(
            user_id=user_id,
            role_name=role_name,
            remover_user_id=current_user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/permissions/{user_id}", response_model=UserPermissionsInfo)
async def get_user_permissions(
    user_id: uuid.UUID,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
):
    """Get detailed permission information for user"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.VIEW_PERMISSIONS
    ):
        if current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' permissions",
            )

    return await permission_service.get_user_permissions_details(user_id)


@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(
    request: PermissionCheckRequest,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
):
    """Check if user has specific permission"""
    await jwt_auth.jwt_required()

    permission_map = {
        "create_roles": RolePermissions.CREATE_ROLES,
        "edit_roles": RolePermissions.EDIT_ROLES,
        "assign_roles": RolePermissions.ASSIGN_ROLES,
        "delete_roles": RolePermissions.DELETE_ROLES,
        "view_permissions": RolePermissions.VIEW_PERMISSIONS,
        "manage_permissions": RolePermissions.MANAGE_PERMISSIONS,
    }

    if request.permission not in permission_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown permission: {request.permission}",
        )

    required_permission = permission_map[request.permission]
    has_permission = await permission_service.check_permission(
        request.user_id, required_permission
    )

    user_permissions = await permission_service.get_user_permissions_details(
        request.user_id
    )

    return PermissionCheckResponse(
        has_permission=has_permission,
        user_permissions=user_permissions["permissions"],
    )


@router.post("/hierarchy/check", response_model=RoleHierarchyResponse)
async def check_role_hierarchy(
    request: RoleHierarchyCheck,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
    user_repo: UserRepoDep,
):
    """Check if user can assign specific role"""
    await jwt_auth.jwt_required()

    can_assign = await permission_service.can_assign_role_to_user(
        assigner_user_id=request.assigner_user_id,
        target_role_name=request.target_role_name,
    )

    reason = None
    if not can_assign:
        assigner_priority = await user_repo.get_highest_role_priority(
            request.assigner_user_id
        )
        target_role = await permission_service.role_type_repo.get_role_by_name(
            request.target_role_name.lower()
        )

        if not target_role:
            reason = f"Role '{request.target_role_name}' does not exist"
        elif not await permission_service.check_permission(
            request.assigner_user_id, RolePermissions.ASSIGN_ROLES
        ):
            reason = "User does not have permission to assign roles"
        elif not RolePriority.can_assign_role(assigner_priority, target_role.priority):
            reason = (
                f"Cannot assign role with priority {target_role.priority} "
                f"(user priority: {assigner_priority})"
            )

    return RoleHierarchyResponse(can_assign=can_assign, reason=reason)


@router.get("/roles", response_model=list[UserRoleInDB])
async def get_user_roles(
    session: SessionDep,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
) -> list[UserRoleInDB]:
    """Get all user roles (admin only)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.MANAGE_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    query = select(Role).options(selectinload(Role.role_type))
    result = await session.execute(query)
    return result.scalars().all()


@router.delete("/roles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_roles(
    user_id: uuid.UUID,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
    user_repo: UserRepoDep,
):
    """Clear all roles from user (admin only)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.MANAGE_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    await user_repo.role_repo.clear_user_roles(user_id)
