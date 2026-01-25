import uuid
from typing import List, Optional, Set
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from constants.permissions import RolePermissions, RolePriority
from db.role_repository import RoleTypeRepository, RoleRepository
from db.repository import UserRepository


class PermissionService:
    """Service for checking permissions and role hierarchy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_type_repo = RoleTypeRepository(session)
        self.role_repo = RoleRepository(session)
    
    async def check_permission(self, user_id: uuid.UUID, required_permission: int) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user_id: User ID to check
            required_permission: Permission bit mask to check
        
        Returns:
            bool: True if user has permission
        """
        if not user_id:
            return False
        
        user_permissions = await self.user_repo.get_user_permissions(user_id)
        return RolePermissions.has_permission(user_permissions, required_permission)
    
    async def check_permissions(self, user_id: uuid.UUID, required_permissions: List[int]) -> bool:
        """
        Check if user has ALL specified permissions
        
        Args:
            user_id: User ID to check
            required_permissions: List of permission bit masks
        
        Returns:
            bool: True if user has all permissions
        """
        for permission in required_permissions:
            if not await self.check_permission(user_id, permission):
                return False
        return True
    
    async def check_any_permission(self, user_id: uuid.UUID, required_permissions: List[int]) -> bool:
        """
        Check if user has ANY of the specified permissions
        
        Args:
            user_id: User ID to check
            required_permissions: List of permission bit masks
        
        Returns:
            bool: True if user has at least one permission
        """
        for permission in required_permissions:
            if await self.check_permission(user_id, permission):
                return True
        return False
    
    async def can_manage_roles(self, user_id: uuid.UUID) -> bool:
        """
        Check if user can manage roles (create, edit, assign)
        
        Args:
            user_id: User ID to check
        
        Returns:
            bool: True if user can manage roles
        """
        return await self.check_permission(user_id, RolePermissions.ASSIGN_ROLES)
    
    async def can_create_roles(self, user_id: uuid.UUID) -> bool:
        """Check if user can create new roles"""
        return await self.check_permission(user_id, RolePermissions.CREATE_ROLES)
    
    async def can_edit_roles(self, user_id: uuid.UUID) -> bool:
        """Check if user can edit existing roles"""
        return await self.check_permission(user_id, RolePermissions.EDIT_ROLES)
    
    async def can_delete_roles(self, user_id: uuid.UUID) -> bool:
        """Check if user can delete roles"""
        return await self.check_permission(user_id, RolePermissions.DELETE_ROLES)
    
    async def can_assign_role_to_user(
        self, 
        assigner_user_id: uuid.UUID, 
        target_role_name: str
    ) -> bool:
        """
        Check if user can assign specific role to another user
        
        Args:
            assigner_user_id: User who wants to assign role
            target_role_name: Role name to assign
        
        Returns:
            bool: True if assignment is allowed
        """
        # Check if assigner has permission to assign roles
        if not await self.can_manage_roles(assigner_user_id):
            return False
        
        # Get assigner's highest priority
        assigner_priority = await self.user_repo.get_highest_role_priority(assigner_user_id)
        
        # Get target role priority
        target_role = await self.role_type_repo.get_role_by_name(target_role_name.lower())
        if not target_role:
            return False
        
        # Check hierarchy
        return RolePriority.can_assign_role(assigner_priority, target_role.priority)
    
    async def can_modify_user_role(
        self, 
        modifier_user_id: uuid.UUID, 
        target_user_id: uuid.UUID,
        new_role_name: Optional[str] = None
    ) -> bool:
        """
        Check if user can modify another user's role
        
        Args:
            modifier_user_id: User who wants to modify role
            target_user_id: User whose role is being modified
            new_role_name: New role name (if changing, not just removing)
        
        Returns:
            bool: True if modification is allowed
        """
        if not await self.can_manage_roles(modifier_user_id):
            return False

        modifier_priority = await self.user_repo.get_highest_role_priority(modifier_user_id)
        
        target_priority = await self.user_repo.get_highest_role_priority(target_user_id)
        
        if target_priority >= modifier_priority:
            return False
        
        if new_role_name:
            return await self.can_assign_role_to_user(modifier_user_id, new_role_name)
        
        return True
    
    async def get_user_permissions_details(self, user_id: uuid.UUID) -> dict:
        """
        Get detailed information about user's permissions
        
        Args:
            user_id: User ID
        
        Returns:
            dict: Detailed permission information
        """
        if not user_id:
            return {
                "user_id": None,
                "roles": [],
                "permissions": [],
                "permissions_mask": 0,
                "highest_priority": 0
            }
        
        user_roles = await self.role_repo.get_user_roles(user_id)
        role_names = [role.role_type.name for role in user_roles if role.role_type]
        
        permissions_mask = await self.user_repo.get_user_permissions(user_id)
        permissions_list = RolePermissions.get_permissions_list(permissions_mask)
        
        highest_priority = await self.user_repo.get_highest_role_priority(user_id)
        
        return {
            "user_id": str(user_id),
            "roles": role_names,
            "permissions": permissions_list,
            "permissions_mask": permissions_mask,
            "highest_priority": highest_priority
        }
    
    async def validate_role_hierarchy(
        self, 
        user_id: uuid.UUID, 
        target_role_priority: int
    ) -> bool:
        """
        Validate if user can work with role of specific priority
        
        Args:
            user_id: User ID to validate
            target_role_priority: Priority of target role
        
        Returns:
            bool: True if user can work with target priority
        """
        user_priority = await self.user_repo.get_highest_role_priority(user_id)
        return RolePriority.can_assign_role(user_priority, target_role_priority)
    
    async def get_role_permissions_info(self, role_name: str) -> dict:
        """
        Get information about role permissions
        
        Args:
            role_name: Role name
        
        Returns:
            dict: Role permissions information
        """
        role = await self.role_type_repo.get_role_by_name(role_name.lower())
        if not role:
            return {}
        
        return {
            "name": role.name,
            "description": role.description,
            "priority": role.priority,
            "permissions": RolePermissions.get_permissions_list(role.permissions),
            "permissions_mask": role.permissions
        }
    
    async def check_system_role_access(self, user_id: uuid.UUID, operation: str) -> bool:
        """
        Check access to system-level operations
        
        Args:
            user_id: User ID
            operation: Type of operation (create_role, edit_role, delete_role, assign_role)
        
        Returns:
            bool: True if access is allowed
        """
        operation_permissions = {
            "create_role": RolePermissions.CREATE_ROLES,
            "edit_role": RolePermissions.EDIT_ROLES,
            "delete_role": RolePermissions.DELETE_ROLES,
            "assign_role": RolePermissions.ASSIGN_ROLES,
            "view_permissions": RolePermissions.VIEW_PERMISSIONS,
            "manage_permissions": RolePermissions.MANAGE_PERMISSIONS
        }
        
        required_permission = operation_permissions.get(operation)
        if required_permission is None:
            return False
        
        return await self.check_permission(user_id, required_permission)


def require_permission(permission: int):
    """Decorator to require specific permission for endpoint"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("current_user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            session = kwargs.get("db")
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            permission_service = PermissionService(session)
            if not await permission_service.check_permission(user_id, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator