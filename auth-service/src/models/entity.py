import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from werkzeug.security import check_password_hash

from db.postgres import Base


class Role(str, enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    SUBSCRIBER = "subscriber"
    USER = "user"


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.USER, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    history = relationship("History", back_populates="user", passive_deletes=True)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


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
