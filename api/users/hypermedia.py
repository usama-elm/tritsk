from uuid import UUID

from litestar import Router, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import (
    ClientRedirect,
    ClientRefresh,
    HTMXTemplate,
    Reswap,
)
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from sqlalchemy.orm import Session

import api.projects.queries as queries_projects
import api.users.commands as commands
import api.users.queries as queries
from api.database import get_db
from api.utils import get_user_by_auth_token, get_user_id_by_auth_token


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_user(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user = commands.create_user(
        session=session,
        username=data["username"],
        name=data["name"],
        aftername=data["aftername"],
        mail=data["mail"],
        password=data["password"],
    )
    if isinstance(user, UUID):
        return ClientRedirect(
            redirect_to="/src/login.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">User and/or password is incorrect</span>',
        )


@get(
    path="/project/{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_users(
    session: Session,
    request: HTMXRequest,
    project_id: int,
    ids: list[int] | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="users.project.get.html",
        context={
            "users": queries.get_users_by_project(
                ids=ids,
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
            "project": queries_projects.get_project_by_id(
                id=project_id,
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
        },
    )


@get(path="/all", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_all_users(
    session: Session,
    request: HTMXRequest,
) -> Template:
    return HTMXTemplate(
        template_name="allusers.get.html",
        context={
            "elements": queries.get_all_users(
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
        },
    )


@get(path="/current", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def current_user(
    session: Session,
    request: HTMXRequest,
) -> Template:
    return HTMXTemplate(
        template_name="current.user.html",
        context={
            "user": get_user_by_auth_token(
                token=request.cookies["X-AUTH"],
                session=session,
            )
        },
    )


@get(
    path="/form/assign/{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_users_form(
    session: Session,
    request: HTMXRequest,
    project_id: int,
) -> Template:
    return HTMXTemplate(
        template_name="list.assign.user.form.html",
        context={
            "users": queries.get_users(
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
            "project_id": project_id,
        },
    )


@post(
    path="/{project_id:int}/assign",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def assign_user_to_project(
    session: Session,
    request: HTMXRequest,
    project_id: int,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRefresh | Reswap:
    assign = commands.add_user_to_project(
        session=session,
        user_id=data["user_id"],
        project_id=project_id,
        role=data["role"],
    )
    if assign == "Success":
        return ClientRefresh()
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">Incorrect info</span>',
        )


hypermedia_users_router = Router(
    path="/hypermedia/users",
    route_handlers=[
        create_user,
        get_all_users,
        get_users,
        get_users_form,
        assign_user_to_project,
        current_user,
    ],
    tags=[
        "Hypermedia",
        "Auth",
    ],
)
