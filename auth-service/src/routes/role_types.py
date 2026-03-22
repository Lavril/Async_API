from fastapi import APIRouter, status, HTTPException
import uuid
from typing import List

from dependencies import AuthJWTDep, PermissionServiceDep, RoleServiceDep
from schemas.entity import (
    RoleTypeCreate,
    RoleTypeUpdate,
    RoleTypeInDB,
)
from constants.permissions import RolePermissions, RolePriority

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleTypeInDB, status_code=status.HTTP_201_CREATED)
async def create_role_type(
    role_create: RoleTypeCreate,
    jwt_auth: AuthJWTDep,
    role_service: RoleServiceDep,
):
    """Create new role type (requires create_roles permission)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    try:
        return await role_service.create_role_type(
            name=role_create.name,
            description=role_create.description,
            permissions=role_create.permissions,
            priority=role_create.priority,
            creator_user_id=current_user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[RoleTypeInDB])
async def get_all_role_types(
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
    role_service: RoleServiceDep,
):
    """Get all role types (requires view_permissions permission)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.VIEW_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view roles",
        )

    return await role_service.get_all_role_types()


@router.get("/{role_name}", response_model=RoleTypeInDB)
async def get_role_type(
    role_name: str,
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
    role_service: RoleServiceDep,
):
    """Get specific role type by name"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.VIEW_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view roles",
        )

    role = await role_service.get_role_by_name(role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )
    return role


@router.put("/{role_id}", response_model=RoleTypeInDB)
async def update_role_type(
    role_id: uuid.UUID,
    role_update: RoleTypeUpdate,
    jwt_auth: AuthJWTDep,
    role_service: RoleServiceDep,
):
    """Update role type (requires edit_roles permission)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    try:
        return await role_service.update_role_type(
            role_id=role_id,
            name=role_update.name,
            description=role_update.description,
            permissions=role_update.permissions,
            priority=role_update.priority,
            editor_user_id=current_user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_type(
    role_id: uuid.UUID,
    jwt_auth: AuthJWTDep,
    role_service: RoleServiceDep,
):
    """Delete role type (requires delete_roles permission)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    try:
        await role_service.delete_role_type(
            role_id=role_id,
            deleter_user_id=current_user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_default_roles(
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
    role_service: RoleServiceDep,
):
    """Initialize default roles (requires create_roles permission)"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.CREATE_ROLES
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to create roles",
        )

    created_roles = await role_service.initialize_default_roles()

    return {
        "message": "Default roles initialized",
        "roles_created": list(created_roles.keys()),
    }


@router.get("/permissions/available", response_model=dict)
async def get_available_permissions(
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
):
    """Get list of all available permissions and their bit values"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.VIEW_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view permissions",
        )

    return RolePermissions.get_permission_names()


@router.get("/hierarchy/levels", response_model=dict)
async def get_role_hierarchy(
    jwt_auth: AuthJWTDep,
    permission_service: PermissionServiceDep,
):
    """Get role priority hierarchy"""
    await jwt_auth.jwt_required()
    claims = await jwt_auth.get_raw_jwt()
    current_user_id = uuid.UUID(claims["user_id"])

    if not await permission_service.check_permission(
        current_user_id, RolePermissions.VIEW_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view role hierarchy",
        )

    return RolePriority.get_priority_map()
