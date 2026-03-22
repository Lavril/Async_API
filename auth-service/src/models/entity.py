import uuid
from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, DateTime, Integer, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from core.security import verify_password

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    # role field removed - use roles table instead
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    roles: Mapped[list["Role"]] = relationship(back_populates="users", passive_deletes=True, cascade="all, delete-orphan")
    history: Mapped[list["History"]] = relationship(back_populates="users", passive_deletes=True, cascade="all, delete-orphan")

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class RoleType(Base):
    __tablename__ = 'role_type'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    permissions: Mapped[int] = mapped_column(Integer, default=0)  # Битовые флаги прав
    priority: Mapped[int] = mapped_column(Integer, default=0)     # Приоритет для иерархии
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    users: Mapped[list["Role"]] = relationship(back_populates="role_type")

    def __init__(self, name: str, description: str | None = None, permissions: int = 0, priority: int = 0) -> None:
        self.name = name
        self.description = description
        self.permissions = permissions
        self.priority = priority

    def __repr__(self) -> str:
        return f"<RoleType {self.name} (priority: {self.priority})>"


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("role_type.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users: Mapped["User"] = relationship(back_populates="roles")
    role_type: Mapped["RoleType"] = relationship(back_populates="users")

    def __init__(self, user_id: uuid.UUID, role_type_id: uuid.UUID) -> None:
        self.user_id = user_id
        self.role_type_id = role_type_id

    def __repr__(self) -> str:
        return f"<Role user_id={self.user_id} role_type_id={self.role_type_id}>"


class History(Base):
    __tablename__ = 'history'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    login_info: Mapped[str | None] = mapped_column(String(255))

    users: Mapped["User"] = relationship(back_populates="history")

    def __init__(self, user_id: uuid.UUID, user_agent: str, login_info: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.login_info = login_info
