import datetime
import re
from typing import List, Optional, Any
from uuid import UUID

import pydantic

from models import User
from custom_types import ModelName
from pydantic import Field

PASSWORD_REGEX = re.compile(
    r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?!_.* ).{8,64}$",
)

class EmailSchema(pydantic.BaseModel):
    email: List[pydantic.EmailStr]
    subject: str
    massage: str


class BaseDeleteResponse(pydantic.BaseModel):
    status: str


class BaseUser(pydantic.BaseModel):
    email: pydantic.EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str


class BaseUserSecure(BaseUser):
    @pydantic.field_validator("password")
    @classmethod
    def secure_password(cls, value: str):
        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit, and be between 8 and 64 characters long",
            )
        return value


class Register(BaseUserSecure):
    pass


class CreateUserResponse(pydantic.BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    registration_time: datetime.datetime
    token: UUID
    task: str


class GetUserResponse(pydantic.BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    registration_time: datetime.datetime
    files: List[int]
    roles: List[str]


class GetUsersResponse(pydantic.BaseModel):
    users: List[Any]


class UpdateUserResponse(GetUserResponse):
    pass


class DeleteUserResponse(BaseDeleteResponse):
    pass


class UpdateUser(pydantic.BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class CreateRight(pydantic.BaseModel):
    model: ModelName
    write: bool
    read: bool
    only_own: bool


class Right(CreateRight):
    id: int


class RightList(pydantic.BaseModel):
    rights: list[Right]
    page: int
    total: int
    count: int


class DeleteRightResponse(BaseDeleteResponse):
    pass


class UpdateRight(pydantic.BaseModel):
    model: Optional[ModelName] = None
    write: Optional[bool] = None
    read: Optional[bool] = None
    only_own: Optional[bool] = None


class Token(pydantic.BaseModel):
    token: UUID


class PaginatedRequestBase(pydantic.BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

    def were_dict(self):
        return super().dict(exclude_none=True, exclude={"page", "limit"})


class PaginatedRightsRequest(PaginatedRequestBase):
    model: Optional[ModelName] = None
    write: Optional[bool] = None
    read: Optional[bool] = None
    only_own: Optional[bool] = None


class PaginatedResponseBase(pydantic.BaseModel):
    page: int
    total: int


class PaginatedRightsResponse(PaginatedResponseBase):
    rights: list[Right]


class Role(pydantic.BaseModel):
    id: int
    name: str
    rights: List[Right]


class CreateRole(pydantic.BaseModel):
    name: str


class UpdateRole(pydantic.BaseModel):
    name: Optional[str] = None
    rights: Optional[List[int]] = None


class CreateRoleResponse(pydantic.BaseModel):
    id: int
    name: str


class UpdateRoleResponse(pydantic.BaseModel):
    id: int
    name: str
    rights: List[int]


class PaginatedRolesRequest(PaginatedRequestBase):
    name: Optional[str] = None


class PaginatedRolesResponse(PaginatedResponseBase):
    roles: List[Role]


class DeleteRoleResponse(BaseDeleteResponse):
    pass


class CreateFile(pydantic.BaseModel):
    name: str
    important: bool
    user_id: Optional[int] = None


class File(pydantic.BaseModel):
    id: int
    name: str
    important: bool
    done: bool
    start_time: datetime.datetime
    finish_time: Optional[datetime.datetime] = None
    user_id: int


class UpdateFileRequest(pydantic.BaseModel):
    name: Optional[str] = None
    important: Optional[bool] = None
    done: Optional[bool] = None


class PaginatedFilesRequest(PaginatedRequestBase):
    name: Optional[str] = None
    important: Optional[bool] = None
    done: Optional[bool] = None
    user_id: Optional[int] = None


class PaginatedFilesResponse(PaginatedResponseBase):
    files: List[File]


class DeleteFileResponse(BaseDeleteResponse):
    pass
