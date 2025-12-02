from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    login: str
    email: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    login: str
    email: str
    first_name: str
    last_name: str


    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)