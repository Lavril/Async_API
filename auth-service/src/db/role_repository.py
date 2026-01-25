import uuid
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.entity import RoleType, Role


class RoleTypeRepository:
    """Repository for working with role_type table"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_role_by_id(self, role_id: uuid.UUID) -> Optional[RoleType]:
        """Get role type by ID"""
        result = await self.session.execute(
            select(RoleType).where(RoleType.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_role_by_name(self, role_name: str) -> Optional[RoleType]:
        """Get role type by name"""
        result = await self.session.execute(
            select(RoleType).where(RoleType.name == role_name)
        )
        return result.scalar_one_or_none()
    
    async def get_all_roles(self) -> List[RoleType]:
        """Get all role types"""
        result = await self.session.execute(
            select(RoleType).order_by(RoleType.priority.asc())
        )
        return result.scalars().all()
    
    async def create_role(self, name: str, description: str = None, 
                         permissions: int = 0, priority: int = 0) -> RoleType:
        """Create new role type"""
        existing_role = await self.get_role_by_name(name)
        if existing_role:
            raise ValueError(f"Role with name '{name}' already exists")
        
        role = RoleType(
            name=name,
            description=description,
            permissions=permissions,
            priority=priority
        )
        
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def update_role(self, role_id: uuid.UUID, name: str = None,
                         description: str = None, permissions: int = None,
                         priority: int = None) -> Optional[RoleType]:
        """Update role type"""
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        update_data = {}
        if name is not None:
            existing_role = await self.get_role_by_name(name)
            if existing_role and existing_role.id != role_id:
                raise ValueError(f"Role with name '{name}' already exists")
            update_data["name"] = name
        
        if description is not None:
            update_data["description"] = description
        
        if permissions is not None:
            update_data["permissions"] = permissions
        
        if priority is not None:
            update_data["priority"] = priority
        
        if update_data:
            await self.session.execute(
                update(RoleType).where(RoleType.id == role_id).values(**update_data)
            )
            await self.session.commit()
            await self.session.refresh(role)
        
        return role
    
    async def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete role type (only if no users have this role)"""
        result = await self.session.execute(
            select(Role).where(Role.role_type_id == role_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("Cannot delete role: some users still have this role")

        result = await self.session.execute(
            delete(RoleType).where(RoleType.id == role_id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_role_permissions(self, role_id: uuid.UUID) -> int:
        """Get permissions for role by ID"""
        role = await self.get_role_by_id(role_id)
        return role.permissions if role else 0
    
    async def get_role_priority(self, role_id: uuid.UUID) -> int:
        """Get priority for role by ID"""
        role = await self.get_role_by_id(role_id)
        return role.priority if role else 0
    
    async def get_role_priority_by_name(self, role_name: str) -> int:
        """Get priority for role by name"""
        role = await self.get_role_by_name(role_name)
        return role.priority if role else 0
    
    async def role_exists(self, role_name: str) -> bool:
        """Check if role exists by name"""
        role = await self.get_role_by_name(role_name)
        return role is not None


class RoleRepository:
    """Repository for working with roles table (user-role assignments)"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_roles(self, user_id: uuid.UUID) -> List[Role]:
        """Get all roles for a user"""
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.role_type))
            .where(Role.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_user_role_names(self, user_id: uuid.UUID) -> List[str]:
        """Get role names for a user"""
        roles = await self.get_user_roles(user_id)
        return [role.role_type.name for role in roles if role.role_type]
    
    async def assign_role_to_user(self, user_id: uuid.UUID, role_type_id: uuid.UUID) -> Role:
        """Assign role to user"""
        existing_role = await self.session.execute(
            select(Role).where(
                Role.user_id == user_id,
                Role.role_type_id == role_type_id
            )
        )
        if existing_role.scalar_one_or_none():
            raise ValueError("User already has this role")
        
        role = Role(user_id=user_id, role_type_id=role_type_id)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        await self.session.refresh(role, ["role_type"])
        return role
    
    async def remove_role_from_user(self, user_id: uuid.UUID, role_type_id: uuid.UUID) -> bool:
        """Remove role from user"""
        result = await self.session.execute(
            delete(Role).where(
                Role.user_id == user_id,
                Role.role_type_id == role_type_id
            )
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_user_role(self, user_id: uuid.UUID, old_role_type_id: uuid.UUID, 
                              new_role_type_id: uuid.UUID) -> Optional[Role]:
        """Update user's role (replace old role with new role)"""
        # Remove old role
        await self.remove_role_from_user(user_id, old_role_type_id)

        return await self.assign_role_to_user(user_id, new_role_type_id)
    
    async def clear_user_roles(self, user_id: uuid.UUID) -> bool:
        """Remove all roles from user"""
        result = await self.session.execute(
            delete(Role).where(Role.user_id == user_id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_users_with_role(self, role_type_id: uuid.UUID) -> List[Role]:
        """Get all users who have specific role"""
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.role_type))
            .where(Role.role_type_id == role_type_id)
        )
        return result.scalars().all()