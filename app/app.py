import datetime

from celery import Celery
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

import schema
from auth import check_access_rights, check_password, get_default_role, hash_password
from crud import add_item, get_item, get_items, get_paginated_items
from depensies import SessionDependency, TokenDependency
from models import Right, Role, File, Token, User
from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_SSL_TLS, CELERY_BROKER_URL, \
    CELERY_RESULT_BACKEND

app = FastAPI(
    title="Uploader API",
    version="1.0",
    description="A simple Uploader API",
)


celery = Celery(__name__,
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
            )
celery.conf.broker_connection_retry_on_startup = True

@celery.task
def send_mail(data: dict) -> str:
    conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=MAIL_PORT,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    html = """
    <p>Thanks for using Uploader</p> 
    """
    message = MessageSchema(
        subject=data['subject'],
        recipients=data['email'],
        body=data['massage'],
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    fm.send_message(message)
    return "OK"


@app.get("/v1/home/")
def home():
    return {"Hello": "World"}


@app.post(
    "/v1/login/",
    response_model=schema.Token,
    tags=["token"],
    summary="Login"
)
async def login(
        user: schema.BaseUser,
        session: SessionDependency
) -> Token:
    user_query = select(User).where(User.email == user.email).execution_options()
    user_model = (await session.scalars(user_query)).first()
    if user_model.roles == []:
        raise HTTPException(
            status_code=401,
            detail="Confirm your email.",
        )
    if user_model and check_password(user.password, user_model.password):
        token = Token(user_id=user_model.id)
        session.add(token)
        await session.commit()
        return schema.Token(token=token.token)
    raise HTTPException(
        status_code=401,
        detail="Invalid email or password",
    )


@app.post(
    "/v1/user/",
    response_model=schema.CreateUserResponse,
    tags=["user"],
    summary="Register user",
)
async def create_user(
    user: schema.Register,
    session: SessionDependency,
) -> schema.CreateUserResponse:
    user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hash_password(
            user.password,
        ),
        roles=[],
    )
    user = await add_item(session, user)
    token = Token(user_id=user.id)
    session.add(token)
    await session.commit()
    data = schema.EmailSchema(
        subject='token of email confirmation',
        email=[user.email],
        massage=str(token.token)
    )
    task = send_mail.apply_async(args=[data.model_dump()])
    return schema.CreateUserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        registration_time=user.registration_time,
        token=token.token,
        task=task.id,
    )


@app.get(
    "/v1/users/",
    response_model=schema.GetUsersResponse,
    tags=["users"],
    summary="Get users"
)
async def get_users(
        session: SessionDependency
):
    result = await session.execute(select(User))
    users = result.unique().scalars().all()
    # users_list = [
    #     {column.name: getattr(row, column.name) for column in User.__table__.columns}
    #     for row in users]
    users_list = []
    for user in users:
        user_dict = {}
        for column in User.__table__.columns:
            user_dict[column.name] = getattr(user, column.name)
        user_dict["roles"] = [role.name for role in user.roles]
        # user_dict["files"] = [file.id for file in user.files],
        user_dict["tokens"] = [token.token for token in user.tokens],
        users_list.append(user_dict)
    return schema.GetUsersResponse(
        users = users_list
    )


@app.get(
    "/v1/user/",
    response_model=schema.GetUserResponse,
    tags=["user"],
    summary="Get user"
)
async def get_user(
        token: TokenDependency,
        session: SessionDependency
) -> schema.GetUserResponse:
    user = await get_item(session, User, token.user_id)
    await check_access_rights(session, token, user, write=False, read=True, owner_field="id")
    return schema.GetUserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        registration_time=user.registration_time,
        files=[file.id for file in user.files],
        roles=[role.name for role in user.roles],
    )


@app.put(
    "/v1/user/",
    response_model=schema.UpdateUserResponse,
    tags=["user"],
    summary="Update user"
)
async def update_user(
        user: schema.UpdateUser,
        token: TokenDependency,
        session: SessionDependency
) -> schema.UpdateUserResponse:
    user_model = await get_item(session, User, token.user_id)
    if user_model.roles == []:
        role = await get_default_role(session)
        setattr(user_model, "roles", [role])
        await session.delete(token)
        await session.commit()
    else:
        await check_access_rights(session, token, user_model, write=True, read=False, owner_field="id")
        for field, value in user.dict(exclude_unset=True).items():
            if field == "password":
                value = hash_password(value)
            setattr(user_model, field, value)
    user_model = await add_item(session, user_model)
    return schema.UpdateUserResponse(
        id=user_model.id,
        email=user_model.email,
        first_name=user.first_name,
        last_name=user.last_name,
        registration_time=user_model.registration_time,
        files=[file.id for file in user_model.files],
        roles=[role.name for role in user_model.roles],
    )


@app.delete(
    "/v1/user/",
    response_model=schema.DeleteUserResponse,
    tags=["user"],
    summary="Delete user"
)
async def delete_user(
        user: schema.BaseUser,
        session: SessionDependency
) -> schema.DeleteUserResponse:
    user_query = select(User).where(User.email == user.email).execution_options()
    user_model = (await session.scalars(user_query)).first()
    if user_model and check_password(user.password, user_model.password):
        await session.delete(user_model)
        await session.commit()
        return schema.DeleteUserResponse(status="deleted")
    raise HTTPException(
        status_code=401,
        detail="Invalid email or password",
    )


@app.get(
    "/v1/right/{right_id}/",
    response_model=schema.Right,
    tags=["right"],
    summary="Get right",
)
async def get_right(
    right_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.Right:
    await check_access_rights(session, token, Right, write=False, read=True)
    right = await get_item(session, Right, right_id)
    return right


@app.get(
    "/v1/right/",
    response_model=schema.PaginatedRightsResponse,
    tags=["right"],
    summary="Get rights",
)
async def get_rights(
    token: TokenDependency,
    session: SessionDependency,
    query_params: schema.PaginatedRightsRequest = Depends(
        schema.PaginatedRightsRequest,
    ),
) -> schema.PaginatedRightsResponse:
    await check_access_rights(session, token, Right, write=False, read=True)
    rights = await get_paginated_items(
        session,
        Right,
        query_params.dict(exclude_none=True, exclude={"page", "limit"}),
        page=query_params.page,
        limit=query_params.limit,
    )
    return schema.PaginatedRightsResponse(
        rights=[schema.Right(**item.dict) for item in rights.items], page=rights.page, total=rights.total
    )


@app.post(
    "/v1/right/",
    response_model=schema.Right,
    tags=["right"],
    summary="Create a right",
)
async def create_right(
    right: schema.CreateRight,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.Right:
    await check_access_rights(session, token, Right, write=True, read=False)
    right = Right(**right.dict())
    right = await add_item(session, right)
    return right


@app.put(
    "/v1/right/{right_id}",
    response_model=schema.Right,
    tags=["right"],
    summary="Update right",
)
async def update_right(
    right_id: int,
    right: schema.UpdateRight,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.Right:
    await check_access_rights(session, token, Right, write=True, read=False)
    right_model = await get_item(session, Right, right_id)
    for field, value in right.dict(exclude_unset=True).items():
        setattr(right_model, field, value)
    right_model = await add_item(session, right_model)
    return right_model


@app.delete(
    "/v1/right/{right_id}",
    response_model=schema.DeleteRightResponse,
    tags=["right"],
    summary="Delete right",
)
async def delete_right(
    right_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.DeleteRightResponse:
    await check_access_rights(session, token, Right, write=True, read=False)
    right = await get_item(session, Right, right_id)
    await session.delete(right)
    await session.commit()
    return schema.DeleteRightResponse(status="deleted")


@app.get(
    "/v1/role/",
    response_model=schema.PaginatedRolesResponse,
    tags=["role"],
    summary="Get roles",
)
async def get_roles(
    token: TokenDependency,
    session: SessionDependency,
    query_params: schema.PaginatedRolesRequest = Depends(
        schema.PaginatedRolesRequest,
    ),
) -> schema.PaginatedRolesResponse:
    await check_access_rights(session, token, Role, write=False, read=True)
    roles = await get_paginated_items(
        session,
        Role,
        query_params.dict(exclude_none=True, exclude={"page", "limit"}),
        page=query_params.page,
        limit=query_params.limit,
    )

    return schema.PaginatedRolesResponse(
        roles=[
            schema.Role(id=item.id, name=item.name, rights=[schema.Right(**right.dict) for right in item.rights])
            for item in roles.items
        ],
        page=roles.page,
        total=roles.total,
    )


@app.get(
    "/v1/role/{role_id}",
    response_model=schema.Role,
    tags=["role"],
    summary="Get role",
)
async def get_role(
    role_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.Role:
    await check_access_rights(session, token, Role, write=False, read=True)
    role = await get_item(session, Role, role_id)
    return role


@app.post(
    "/v1/role/",
    response_model=schema.CreateRoleResponse,
    tags=["role"],
    summary="Create role",
)
async def create_role(
    role: schema.CreateRole,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.CreateRoleResponse:
    await check_access_rights(session, token, Role, write=True, read=False)
    role = Role(**role.dict())
    role = await add_item(session, role)
    return schema.CreateRoleResponse(
        id=role.id,
        name=role.name,
    )


@app.put(
    "/v1/role/{role_id}",
    response_model=schema.UpdateRoleResponse,
    tags=["role"],
    summary="Update role",
)
async def update_role(
    role_id: int,
    role: schema.UpdateRole,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.UpdateRoleResponse:
    await check_access_rights(session, token, Role, write=True, read=False)
    role_model = await get_item(session, Role, role_id)

    if role.rights:
        await check_access_rights(session, token, Right, write=False, read=True)
        rights = await get_items(session, Right, role.rights)
        role_model.rights = rights

    for field, value in role.dict(exclude_unset=True, exclude={"rights"}).items():
        setattr(role_model, field, value)

    role_model = await add_item(session, role_model)

    return schema.UpdateRoleResponse(
        id=role_model.id,
        name=role_model.name,
        rights=[right.id for right in role_model.rights],
    )


@app.delete(
    "/v1/role/{role_id}",
    response_model=schema.DeleteRoleResponse,
    tags=["role"],
    summary="Delete role",
)
async def delete_role(
    role_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.DeleteRoleResponse:
    await check_access_rights(session, token, Role, write=True, read=False)
    role = await get_item(session, Role, role_id)
    await session.delete(role)
    await session.commit()
    return schema.DeleteRoleResponse(status="deleted")


@app.get(
    "/v1/file/",
    response_model=schema.PaginatedFilesResponse,
    tags=["file"],
    summary="Get files",
)
async def get_files(
    token: TokenDependency,
    session: SessionDependency,
    query_params: schema.PaginatedFilesRequest = Depends(
        schema.PaginatedFilesRequest,
    ),
) -> schema.PaginatedFilesResponse:
    params = query_params.dict(exclude_none=True, exclude={"page", "limit"})
    if check_access_rights(session, token, File, write=False, read=True, raise_exception=False):
        #  Если пользователь может видеть только свои задачи, то добавляем это условие
        params["user_id"] = token.user_id

    files = await get_paginated_items(
        session,
        File,
        params,
        page=query_params.page,
        limit=query_params.limit,
    )

    return schema.PaginatedFilesResponse(
        files=[schema.File(**item.dict) for item in files.items], page=files.page, total=files.total
    )


@app.get(
    "/v1/file/{file_id}",
    response_model=schema.File,
    tags=["file"],
    summary="Get file",
)
async def get_file(
    file_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.File:
    file = await get_item(session, File, file_id)
    await check_access_rights(session, token, file, write=False, read=True, owner_field="user_id")
    return file


@app.post(
    "/v1/file/",
    response_model=schema.File,
    tags=["file"],
    summary="Create file",
)
async def create_file(
    file: schema.CreateFile,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.File:
    if not file.user_id:
        file.user_id = token.user_id
    file = File(**file.dict())
    await check_access_rights(session, token, file, write=True, read=False, owner_field="user_id")
    file = await add_item(session, file)
    return file


@app.put(
    "/v1/file/{file_id}",
    response_model=schema.File,
    tags=["file"],
    summary="Update file",
)
async def update_file(
    file_id: int,
    file: schema.UpdateFileRequest,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.File:
    file_model = await get_item(session, File, file_id)
    await check_access_rights(session, token, file_model, write=True, read=False, owner_field="user_id")
    payload = file.dict(exclude_unset=True)
    if "done" in payload:
        payload["finish_time"] = datetime.datetime.now()
    for field, value in payload.items():
        setattr(file_model, field, value)
    file_model = await add_item(session, file_model)
    return file_model


@app.delete(
    "/v1/file/{file_id}",
    response_model=schema.DeleteFileResponse,
    tags=["file"],
    summary="Delete file",
)
async def delete_file(
    file_id: int,
    token: TokenDependency,
    session: SessionDependency,
) -> schema.DeleteFileResponse:
    file = await get_item(session, File, file_id)
    await check_access_rights(session, token, file, write=True, read=False, owner_field="user_id")
    await session.delete(file)
    await session.commit()
    return schema.DeleteFileResponse(status="deleted")
