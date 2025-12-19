from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr

from models.entity import UserRole


class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    login: str
    email: EmailStr
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    user_id: UUID
    role: UserRole


class RoleInDB(BaseModel):
    id: UUID
    user_id: UUID
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: UserRole
