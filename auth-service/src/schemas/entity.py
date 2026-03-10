import re
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, constr, Field
from models.entity import User, RoleType, Role
from constants.permissions import RolePermissions


class UserBase(BaseModel):
    login: str
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=10, max_length=72)
    role_name: str = Field(default="user", description="Role name to assign to user")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('login')
    def validate_login(cls, v):
        if len(v) < 3:
            raise ValueError('Login must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Login can only contain letters, numbers and underscores')
        return v

    @field_validator('role_name')
    def validate_role_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Role name must be at least 2 characters')
        return v.lower().strip()


class UserInDB(UserBase):
    id: UUID
    roles: List[str] = Field(default=[], description="List of role names")
    permissions: int = Field(default=0, description="Combined permissions mask")
    highest_role_priority: int = Field(default=0, description="Highest role priority")
    primary_role: str = Field(default="user", description="Primary role name")

    model_config = ConfigDict(from_attributes=True)


class UserChangePassword(BaseModel):
    current_password: str
    new_password: constr(min_length=10)

    @field_validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserChangeLogin(BaseModel):
    new_login: str

    @field_validator('new_login')
    def validate_new_login(cls, v):
        if len(v) < 3:
            raise ValueError('Login must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Login can only contain letters, numbers and underscores')
        return v


class LoginSchema(BaseModel):
    login: str
    password: str


class RoleTypeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    permissions: int = Field(0, description="Bit mask of permissions")
    priority: int = Field(0, description="Role priority for hierarchy")

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Role name must be at least 2 characters')
        if not re.match(r'^[a-z_]+$', v.lower().strip()):
            raise ValueError('Role name can only contain lowercase letters and underscores')
        return v.lower().strip()


class RoleTypeCreate(RoleTypeBase):
    pass


class RoleTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[int] = Field(None)
    priority: Optional[int] = Field(None)


class RoleTypeInDB(RoleTypeBase):
    id: UUID
    created_at: str

    @field_validator('created_at', mode='before')
    @classmethod
    def format_datetime(cls, v):
        if isinstance(v, str):
            return v
        return v.isoformat() if v else None

    model_config = ConfigDict(from_attributes=True)


class UserRoleAssign(BaseModel):
    role_name: str = Field(..., description="Role name to assign")
    user_id: UUID = Field(..., description="User ID")


class UserRoleInDB(BaseModel):
    id: UUID
    user_id: UUID
    role_type_id: UUID
    assigned_at: str
    role_type: Optional[RoleTypeInDB] = None

    @field_validator('assigned_at', mode='before')
    @classmethod
    def format_datetime(cls, v):
        if isinstance(v, str):
            return v
        return v.isoformat() if v else None

    model_config = ConfigDict(from_attributes=True)


class UserPermissionsInfo(BaseModel):
    user_id: str
    roles: List[str]
    permissions: List[str]
    permissions_mask: int
    highest_role_priority: int

    model_config = ConfigDict(from_attributes=True)


class PermissionCheckRequest(BaseModel):
    user_id: UUID
    permission: str = Field(..., description="Permission to check (e.g., 'create_roles')")


class PermissionCheckResponse(BaseModel):
    has_permission: bool
    user_permissions: List[str]


class RoleHierarchyCheck(BaseModel):
    assigner_user_id: UUID
    target_role_name: str


class RoleHierarchyResponse(BaseModel):
    can_assign: bool
    reason: Optional[str] = None