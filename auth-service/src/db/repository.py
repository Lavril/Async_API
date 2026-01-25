import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.entity import User, History, Role, RoleType
from core.security import get_password_hash, verify_password
from .role_repository import RoleRepository, RoleTypeRepository


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)
        self.role_type_repo = RoleTypeRepository(session)

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID with roles"""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.role_type))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_login(self, login: str) -> Optional[User]:
        """Get user by login with roles"""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.role_type))
            .where(User.login == login)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        login: str,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        role_name: str = "user"
    ) -> User:
        """Create new user with specified role"""
        hashed_password = get_password_hash(password)
        user = User(
            login=login,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.flush()

        role_type = await self.role_type_repo.get_role_by_name(role_name)
        if not role_type:
            role_type = await self.role_type_repo.get_role_by_name("user")
            if not role_type:
                raise ValueError("Default 'user' role not found in database")

        await self.role_repo.assign_role_to_user(user.id, role_type.id)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Update user password"""
        hashed_password = get_password_hash(new_password)
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password=hashed_password)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def update_user_login(self, user_id: uuid.UUID, new_login: str) -> bool:
        """Update user login"""
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(login=new_login)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def verify_user_password(self, user_id: uuid.UUID, password: str) -> bool:
        """Verify user password"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        return verify_password(password, user.password)

    async def get_user_role_names(self, user_id: uuid.UUID) -> list[str]:
        """Get list of role names for user"""
        return await self.role_repo.get_user_role_names(user_id)

    async def get_user_permissions(self, user_id: uuid.UUID) -> int:
        """Get combined permissions for all user roles"""
        roles = await self.role_repo.get_user_roles(user_id)
        permissions = 0
        for role in roles:
            if role.role_type:
                permissions |= role.role_type.permissions
        return permissions

    async def get_highest_role_priority(self, user_id: uuid.UUID) -> int:
        """Get highest priority among all user roles"""
        roles = await self.role_repo.get_user_roles(user_id)
        if not roles:
            return 0
        return max(role.role_type.priority for role in roles if role.role_type)

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> Role:
        """Assign role to user by role name"""
        role_type = await self.role_type_repo.get_role_by_name(role_name)
        if not role_type:
            raise ValueError(f"Role '{role_name}' not found")
        
        return await self.role_repo.assign_role_to_user(user_id, role_type.id)

    async def remove_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        """Remove role from user by role name"""
        role_type = await self.role_type_repo.get_role_by_name(role_name)
        if not role_type:
            raise ValueError(f"Role '{role_name}' not found")
        
        return await self.role_repo.remove_role_from_user(user_id, role_type.id)


class LoginHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_login_record(
        self,
        user_id: uuid.UUID,
        user_agent: str = "",
        login_info: str = ""
    ) -> History:
        """Create login history record"""
        record = History(
            user_id=user_id,
            user_agent=user_agent or "",
            login_info=login_info or ""
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_user_login_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[History]:
        """Get user login history"""
        result = await self.session.execute(
            select(History)
            .where(History.user_id == user_id)
            .order_by(History.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(History.users))
        )
        return result.scalars().all()
