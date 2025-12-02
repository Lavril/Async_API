import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    roles = relationship("Role", back_populates="user", passive_deletes=True)
    history = relationship("History", back_populates="user", passive_deletes=True)

    def __init__(self, login: str, email: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="roles")

    def __init__(self, user_id: uuid.UUID, role: str) -> None:
        self.user_id = user_id
        self.role = role

    def __repr__(self) -> str:
        return f'<Role {self.role}>'


class History(Base):
    __tablename__ = 'history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_agent = Column(String(255), nullable=False)
    login_time = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    login_info = Column(String(255))

    user = relationship("User", back_populates="history")

    def __init__(self, user_id: uuid.UUID, user_agent: str, login_info: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.login_info = login_info
