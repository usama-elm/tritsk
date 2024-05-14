from litestar import Router, delete, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import (
    ClientRedirect,
    ClientRefresh,
    Reswap,
)
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from sqlalchemy.orm import Session

import api.projects.commands as commands
import api.projects.queries as queries
from api.database import get_db
from api.projects.services import execute_template
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_projects(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
) -> Template:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    projects_managed = queries.get_projects_by_role(
        ids=ids,
        session=session,
        role=["chief", "collaborator"],
        user_id=user_id,
    )
    projects = queries.get_projects_by_role(
        ids=ids,
        session=session,
        role=["user"],
        user_id=user_id,
    )
    context = {
        "projects_managed": projects_managed,
        "projects": projects,
    }

    return execute_template(session, request, "projects.get.html", context)


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_project(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    description = data["description"] if data["description"] else None
    project = commands.create_project(
        session=session,
        user_id=user_id,
        name=data["name"],
        description=description,
    )

    match project:
        case int():
            return ClientRedirect(redirect_to="/src/projects.html")
        case _:
            return Reswap(
                method="innerHTML",
                content='<span id="error">One and/or more elements of the form are incorrect</span>',
            )


@delete(
    path="/{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=200,
)
def delete_task(
    session: Session,
    request: HTMXRequest,
    project_id: int,
) -> ClientRefresh:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    commands.delete_project(
        session=session,
        user_id=user_id,
        project_id=project_id,
    )
    return ClientRefresh()


@get(
    path="/edit",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_project_edit_form(
    request: HTMXRequest,
    project_id: int,
) -> Template:
    context = {"id": project_id}
    return execute_template(None, request, "project.edit.form.html", context)


@post(
    path="{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def update_project(
    session: Session,
    request: HTMXRequest,
    project_id: int,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    task_edit = commands.update_project(
        session=session,
        user_id=user_id,
        project_id=project_id,
        name=data["name"],
        description=data["description"],
    )

    match task_edit:
        case int():
            return ClientRedirect(redirect_to="/src/main.html")
        case _:
            return Reswap(
                method="innerHTML",
                content='<span id="error">One and/or more elements of the form are incorrect</span>',
            )


@get(path="/list", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_projects_list(session: Session, request: HTMXRequest) -> Template:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    projects = queries.get_projects(
        ids=None,
        session=session,
        user_id=user_id,
        role=["chief", "collaborator"],
    )
    context = {"projects": projects}
    return execute_template(session, request, "list.projects.get.html", context)


hypermedia_projects_router = Router(
    path="/hypermedia/projects",
    route_handlers=[
        get_projects,
        create_project,
        delete_task,
        get_project_edit_form,
        update_project,
        get_projects_list,
    ],
    tags=[
        "Projects",
    ],
)
