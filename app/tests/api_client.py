from typing import Dict, List, Literal, NamedTuple, Optional, Union

import requests
from sqlalchemy import UUID

JsonType = Dict[str, Union[str, bool, int, List[int], "JsonType", List["JsonType"]]]


HTTP_METHOD = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
RESPONSE_TYPE = Literal["json", "text"]


class HttpError(Exception):
    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description

    def __str__(self):
        return f"{self.status_code=}\n{self.description=}"


class BaseDeleteResponse(NamedTuple):
    status: str


class TokenResponse(NamedTuple):
    token: str


class CreateUserResponse(NamedTuple):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    registration_time: str
    token: UUID


class GetUserResponse(NamedTuple):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    registration_time: str
    files: List[int]
    roles: List[int]


class UpdateUserResponse(GetUserResponse):
    pass


class DeleteUserResponse(BaseDeleteResponse):
    status: str


class BaseRightResponse(NamedTuple):
    id: int
    model: str
    write: bool
    read: bool
    only_own: bool


class GetRightResponse(BaseRightResponse):
    pass


class GetRightsResponse(NamedTuple):
    rights: list[BaseRightResponse]
    page: int
    total: int


class CreateRightResponse(BaseRightResponse):
    pass


class UpdateRightResponse(BaseRightResponse):
    pass


class DeleteRightResponse(BaseDeleteResponse):
    status: str


class GetRoleResponse(NamedTuple):
    id: int
    name: str
    rights: List[GetRightResponse]


class GetRolesResponse(NamedTuple):
    roles: List[GetRoleResponse]
    page: int
    total: int


class CreateRoleResponse(NamedTuple):
    id: int
    name: str


class UpdateRoleResponse(NamedTuple):
    id: int
    name: str
    rights: List[GetRightResponse]


class DeleteRoleResponse(BaseDeleteResponse):
    pass


class GetFileResponse(NamedTuple):
    id: int
    name: str
    done: bool
    important: bool
    user_id: int
    start_time: str
    finish_time: str


class GetFilesResponse(NamedTuple):
    files: List[GetFileResponse]
    page: int
    total: int


class CreateFileResponse(GetFileResponse):
    pass


class UpdateFileResponse(GetFileResponse):
    pass


class DeleteFileResponse(BaseDeleteResponse):
    pass


class FileApiClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = requests.Session()
        self.headers: Dict[str, str] = {}

    def _call(
        self,
        http_method: HTTP_METHOD,
        api_method: str,
        json: Optional[JsonType] = None,
        **kwargs,
    ) -> JsonType:
        headers = {**kwargs.pop("headers", {}), **self.headers}
        response = getattr(self.client, http_method.lower())(
            f"{self.api_url}{api_method}", json=json, headers=headers, **kwargs
        )

        if response.status_code >= 400:
            raise HttpError(response.status_code, response.text)

        return response.json()

    def login(self, email: str, password: str) -> TokenResponse:
        return TokenResponse(
            **self._call("POST", "/v1/login/", json={"email": email, "password": password})  # type: ignore
        )

    def auth(self, email: str, password: str) -> None:
        token = self.login(email, password).token
        self.headers["x-token"] = token

    def create_user(self, email: str, password: str) -> CreateUserResponse:
        return CreateUserResponse(
            **self._call(
                "POST",
                "/v1/user",
                json={"email": email, "password": password},  # type: ignore
            )
        )

    def confirm_user(self, email=None, password=None) -> UpdateUserResponse:
        token = self.create_user(email, password).token
        self.headers["x-token"] = token
        return UpdateUserResponse(
            **self._call("PUT", f"/v1/user/", json={})  # type: ignore
        )

    def get_user(self) -> GetUserResponse:
        return GetUserResponse(**self._call("GET", f"/v1/user/"))  # type: ignore

    def update_user(self, email=None, password=None) -> UpdateUserResponse:
        params = {}
        if email is not None:
            params["email"] = email
        if password is not None:
            params["password"] = password
        return UpdateUserResponse(
            **self._call("PUT", f"/v1/user/", json=params)  # type: ignore
        )

    def delete_user(self, email=None, password=None) -> DeleteUserResponse:
        params = {}
        if email is not None:
            params["email"] = email
        if password is not None:
            params["password"] = password
        return DeleteUserResponse(**self._call("DELETE", f"/v1/user/", json=params))  # type: ignore

    def create_right(self, model: str, write: bool, read: bool, only_own: bool) -> CreateRightResponse:
        return CreateRightResponse(
            **self._call(
                "POST",
                "/v1/right",
                json={"model": model, "write": write, "read": read, "only_own": only_own},  # type: ignore
            )
        )

    def get_right(self, right_id: int) -> GetRightResponse:
        return GetRightResponse(**self._call("GET", f"/v1/right/{right_id}/"))  # type: ignore

    def get_rights(
        self, model: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None
    ) -> GetRightsResponse:
        params: Dict[str, int | str] = {}

        if model is not None:
            params["model"] = model
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        response = self._call("GET", "/v1/right/", params=params)
        response["rights"] = [BaseRightResponse(**right) for right in response["rights"]]  # type: ignore
        return GetRightsResponse(**response)  # type: ignore

    def update_right(self, right_id: int, model=None, write=None, read=None, only_own=None) -> UpdateRightResponse:
        params = {}
        if model is not None:
            params["model"] = model
        if write is not None:
            params["write"] = write
        if read is not None:
            params["read"] = read
        if only_own is not None:
            params["only_own"] = only_own
        return UpdateRightResponse(
            **self._call("PUT", f"/v1/right/{right_id}", json=params)  # type: ignore
        )

    def delete_right(self, right_id: int) -> DeleteRightResponse:
        return DeleteRightResponse(
            **self._call("DELETE", f"/v1/right/{right_id}")  # type: ignore
        )

    def get_role(self, role_id: int) -> GetRoleResponse:
        response = self._call("GET", f"/v1/role/{role_id}")
        response["rights"] = [GetRightResponse(**right) for right in response["rights"]]  # type: ignore
        return GetRoleResponse(**response)  # type: ignore

    def get_roles(
        self, name: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None
    ) -> GetRolesResponse:
        params: Dict[str, str | int] = {}
        if name is not None:
            params["name"] = name
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        response = self._call("GET", "/v1/role/", params=params)
        for role in response["roles"]:  # type: ignore
            role["rights"] = [GetRightResponse(**right) for right in role["rights"]]  # type: ignore
        response["roles"] = [GetRoleResponse(**role) for role in response["roles"]]  # type: ignore
        return GetRolesResponse(**response)  # type: ignore

    def create_role(self, name: str) -> CreateRoleResponse:
        return CreateRoleResponse(
            **self._call("POST", "/v1/role", json={"name": name})  # type: ignore
        )

    def update_role(
        self, role_id: int, name: Optional[str] = None, rights: Optional[List[int]] = None
    ) -> UpdateRoleResponse:
        params: Dict[str, str | List[int]] = {}
        if name is not None:
            params["name"] = name
        if rights is not None:
            params["rights"] = rights
        return UpdateRoleResponse(
            **self._call("PUT", f"/v1/role/{role_id}", json=params)  # type: ignore
        )

    def delete_role(self, role_id: int) -> DeleteRoleResponse:
        return DeleteRoleResponse(**self._call("DELETE", f"/v1/role/{role_id}"))  # type: ignore

    def get_file(self, file_id: int) -> GetFileResponse:
        return GetFileResponse(**self._call("GET", f"/v1/file/{file_id}"))  # type: ignore

    def get_files(self, page: Optional[int] = None, limit: Optional[int] = None) -> GetFilesResponse:
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        response = self._call("GET", "/v1/file/", params=params)
        response["files"] = [GetFileResponse(**file) for file in response["files"]]  # type: ignore
        return GetFilesResponse(**response)  # type: ignore

    def create_file(
        self, name: str, important: Optional[bool] = False, user_id: Optional[int] = None
    ) -> CreateFileResponse:
        params: Dict[str, str | bool | int] = {"name": name, "important": important}  # type: ignore
        if user_id is not None:
            params["user_id"] = user_id
        return CreateFileResponse(
            **self._call(
                "POST",
                "/v1/file/",
                json=params,  # type: ignore
            )
        )

    def update_file(
        self, file_id: int, name: Optional[str] = None, done: Optional[bool] = None, important: Optional[bool] = None
    ) -> UpdateFileResponse:
        params: Dict[str, str | bool] = {}
        if name is not None:
            params["name"] = name
        if done is not None:
            params["done"] = done
        if important is not None:
            params["important"] = important

        return UpdateFileResponse(
            **self._call("PUT", f"/v1/file/{file_id}", json=params)  # type: ignore
        )

    def delete_file(self, file_id: int) -> DeleteFileResponse:
        return DeleteFileResponse(
            **self._call("DELETE", f"/v1/file/{file_id}")  # type: ignore
        )
