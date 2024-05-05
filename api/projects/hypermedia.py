from litestar import Router, delete, get, post
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

import api.projects.commands as commands
import api.projects.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_projects(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="projects.get.html",
        context={
            "tasks": queries.get_tasks(
                ids=ids,
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
        },
    )


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_project(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    project = commands.create_project(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        name=data["name"],
        description=data["description"] if data["description"] else None,
    )
    if isinstance(project, int):
        return ClientRedirect(
            redirect_to="/src/main.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">One and/or more elements of the form are incorrect</span>',
        )


@delete(
    path="{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=200,
)
def delete_task(
    session: Session,
    request: HTMXRequest,
    project_id: int,
) -> ClientRefresh:
    commands.delete_project(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        project_id=project_id,
    )
    return ClientRefresh()


@get(
    path="/form/{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_project_edit_form(
    request: HTMXRequest,
    project_id: int,
) -> Template:
    return HTMXTemplate(
        template_name="project.edit.form.html",
        context={"id": project_id},
    )


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
    task_edit = commands.update_project(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        project_id=project_id,
        name=data["name"],
        description=data["description"],
    )
    if isinstance(task_edit, int):
        return ClientRedirect(
            redirect_to="/src/main.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">One and/or more elements of the form are incorrect</span>',
        )
    ...


hypermedia_projects_router = Router(
    path="/hypermedia/projects",
    route_handlers=[
        get_projects,
        create_project,
        delete_task,
        get_project_edit_form,
        update_project,
    ],
    tags=[
        "Hypermedia",
        "Projects",
    ],
)
