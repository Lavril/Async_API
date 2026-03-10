import uuid
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import RoleType
from db.role_repository import RoleTypeRepository, RoleRepository
from constants.permissions import RolePermissions, RolePriority, InitialRoles
from db.postgres import get_session


class RoleService:
    """Service for managing role types with business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_type_repo = RoleTypeRepository(session)
        self.role_repo = RoleRepository(session)
    
    async def create_role_type(
        self, 
        name: str, 
        description: str = None,
        permissions: int = 0,
        priority: int = 0,
        creator_user_id: uuid.UUID = None
    ) -> RoleType:
        """
        Create new role type with permission checks
        
        Args:
            name: Role name (must be unique)
            description: Role description
            permissions: Bit mask of permissions
            priority: Role priority for hierarchy
            creator_user_id: ID of user creating this role (for permission check)
        
        Returns:
            RoleType: Created role type
        
        Raises:
            HTTPException: If user lacks permissions or role exists
        """
        if creator_user_id:
            creator_permissions = await self._get_user_permissions(creator_user_id)
            if not RolePermissions.has_permission(creator_permissions, RolePermissions.CREATE_ROLES):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to create roles"
                )

        if creator_user_id and priority > 0:
            creator_priority = await self._get_user_priority(creator_user_id)
            if priority >= creator_priority:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot create role with priority equal or higher than your own"
                )

        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name must be at least 2 characters"
            )

        try:
            return await self.role_type_repo.create_role(
                name=name.lower().strip(),
                description=description,
                permissions=permissions,
                priority=priority
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def update_role_type(
        self,
        role_id: uuid.UUID,
        name: str = None,
        description: str = None,
        permissions: int = None,
        priority: int = None,
        editor_user_id: uuid.UUID = None
    ) -> RoleType:
        """
        Update existing role type with permission checks
        
        Args:
            role_id: ID of role to update
            name: New role name
            description: New description
            permissions: New permissions
            priority: New priority
            editor_user_id: ID of user updating role
        
        Returns:
            RoleType: Updated role type
        """
        if editor_user_id:
            editor_permissions = await self._get_user_permissions(editor_user_id)
            if not RolePermissions.has_permission(editor_permissions, RolePermissions.EDIT_ROLES):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to edit roles"
                )

        current_role = await self.role_type_repo.get_role_by_id(role_id)
        if not current_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        if editor_user_id and priority is not None:
            editor_priority = await self._get_user_priority(editor_user_id)
            if priority >= editor_priority:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot set priority equal or higher than your own"
                )

        if name and len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name must be at least 2 characters"
            )
        
        try:
            return await self.role_type_repo.update_role(
                role_id=role_id,
                name=name.lower().strip() if name else None,
                description=description,
                permissions=permissions,
                priority=priority
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def delete_role_type(
        self, 
        role_id: uuid.UUID,
        deleter_user_id: uuid.UUID = None
    ) -> bool:
        """
        Delete role type with permission checks
        
        Args:
            role_id: ID of role to delete
            deleter_user_id: ID of user deleting role
        
        Returns:
            bool: True if deleted successfully
        """
        if deleter_user_id:
            deleter_permissions = await self._get_user_permissions(deleter_user_id)
            if not RolePermissions.has_permission(deleter_permissions, RolePermissions.DELETE_ROLES):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to delete roles"
                )

        role = await self.role_type_repo.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        if role.name in ['user', 'superuser']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system roles"
            )
        
        try:
            return await self.role_type_repo.delete_role(role_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def assign_role_to_user(
        self,
        user_id: uuid.UUID,
        role_name: str,
        assigner_user_id: uuid.UUID = None
    ):
        """
        Assign role to user with permission and hierarchy checks
        
        Args:
            user_id: User to assign role to
            role_name: Role name to assign
            assigner_user_id: User performing assignment
        
        Returns:
            Role: Assigned role
        """
        if assigner_user_id:
            assigner_permissions = await self._get_user_permissions(assigner_user_id)
            if not RolePermissions.has_permission(assigner_permissions, RolePermissions.ASSIGN_ROLES):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to assign roles"
                )

        target_role = await self.role_type_repo.get_role_by_name(role_name.lower())
        if not target_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found"
            )

        if assigner_user_id:
            assigner_priority = await self._get_user_priority(assigner_user_id)
            if not RolePriority.can_assign_role(assigner_priority, target_role.priority):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot assign role '{role_name}' - priority too high"
                )
        
        try:
            return await self.role_repo.assign_role_to_user(user_id, target_role.id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def remove_role_from_user(
        self,
        user_id: uuid.UUID,
        role_name: str,
        remover_user_id: uuid.UUID = None
    ) -> bool:
        """
        Remove role from user with permission checks
        
        Args:
            user_id: User to remove role from
            role_name: Role name to remove
            remover_user_id: User performing removal
        
        Returns:
            bool: True if removed successfully
        """
        if remover_user_id:
            remover_permissions = await self._get_user_permissions(remover_user_id)
            if not RolePermissions.has_permission(remover_permissions, RolePermissions.ASSIGN_ROLES):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to manage user roles"
                )

        target_role = await self.role_type_repo.get_role_by_name(role_name.lower())
        if not target_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found"
            )

        if remover_user_id:
            remover_priority = await self._get_user_priority(remover_user_id)
            if not RolePriority.can_assign_role(remover_priority, target_role.priority):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot remove role '{role_name}' - priority too high"
                )
        
        return await self.role_repo.remove_role_from_user(user_id, target_role.id)
    
    async def get_all_role_types(self) -> List[RoleType]:
        """Get all role types ordered by priority"""
        return await self.role_type_repo.get_all_roles()
    
    async def get_role_by_name(self, role_name: str) -> Optional[RoleType]:
        """Get role type by name"""
        return await self.role_type_repo.get_role_by_name(role_name.lower())
    
    async def initialize_default_roles(self) -> Dict[str, RoleType]:
        """Initialize default roles from InitialRoles configuration"""
        created_roles = {}
        
        for role_data in InitialRoles.get_roles_data():
            try:
                existing_role = await self.role_type_repo.get_role_by_name(role_data["name"])
                if existing_role:
                    created_roles[role_data["name"]] = existing_role
                    continue

                role = await self.role_type_repo.create_role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                    priority=role_data["priority"]
                )
                created_roles[role_data["name"]] = role
                
            except Exception as e:
                print(f"Error creating role {role_data['name']}: {e}")
        
        return created_roles
    
    async def _get_user_permissions(self, user_id: uuid.UUID) -> int:
        """Get combined permissions for user"""
        from db.repository import UserRepository
        user_repo = UserRepository(self.session)
        return await user_repo.get_user_permissions(user_id)
    
    async def _get_user_priority(self, user_id: uuid.UUID) -> int:
        """Get highest role priority for user"""
        from db.repository import UserRepository
        user_repo = UserRepository(self.session)
        return await user_repo.get_highest_role_priority(user_id)