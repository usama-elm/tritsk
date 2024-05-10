from datetime import datetime

from litestar import Router, delete, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import (
    ClientRedirect,
    ClientRefresh,
    HTMXTemplate,
    Reswap,
    Retarget,
)
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template
from sqlalchemy import exc
from sqlalchemy.orm import Session

import api.tasks.commands as commands
import api.tasks.queries as queries
import api.tasks.subtasks.queries as subtask_queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(
    path="/",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_tasks(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
    project_id: int | None = None,
    priority: int | None = None,
    status: int | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="tasks.get.html",
        context={
            "tasks": queries.get_tasks(
                ids=ids,
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
                project_id=project_id,
                priority=priority,
            )
        },
    )


@get(
    path="/{task_id:int}/subtasks",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_subtasks_by_task(
    session: Session,
    request: HTMXRequest,
    task_id: int,
    ids: list[int] | None = None,
    status: int | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="subtasks.get.html",
        context={
            "subtasks": subtask_queries.get_subtasks_by_task(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
                task_id=task_id,
                ids=ids,
                status_id=status,
            )
        },
    )


@get(
    path="/tasks_by_project",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_tasks_projects(
    session: Session,
    request: HTMXRequest,
) -> Template:
    return HTMXTemplate(
        template_name="projects.tasks.get.html",
        context={
            "elements": queries.get_tasks_by_project_user(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
            )
        },
    )


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_task(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    task = commands.create_task(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        title=data["title"],
        content=data["content"] if data["content"] else None,
        priority_id=data["priority"],
        deadline=(
            datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M").date()
            if data["deadline"] != ""
            else None
        ),
        project_id=data["project_id"],
        status_id=data["status"],
    )
    if isinstance(task, int):
        return ClientRedirect(
            redirect_to="/src/main.html",
        )
    else:
        return Reswap(
            method="outerHTML",
            content='<span id="error">One and/or more elements of the form are incorrect</span>',
        )


@delete(
    path="{id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=200,
)
def delete_task(
    session: Session,
    request: HTMXRequest,
    id: int,
) -> ClientRefresh:
    commands.delete_task(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        id=id,
    )
    return ClientRefresh()


@get(
    path="/form/{id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_task_edit_form(
    request: HTMXRequest,
    id: int,
) -> Template:
    return HTMXTemplate(
        template_name="tasks.edit.form.html",
        context={"id": id},
    )


@get(
    path="/assign/form/{project_id:int}/{user_id:str}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_assign_tasks(
    session: Session,
    request: HTMXRequest,
    project_id: int,
    user_id: str,
) -> Template:
    return HTMXTemplate(
        template_name="list.tasks.project.user.get.html",
        context={
            "tasks": queries.get_tasks(
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
                project_id=project_id,
                ids=None,
            ),
            "project_id": project_id,
            "user_id": user_id,
        },
    )


@post(path="{id:int}", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def update_task(
    session: Session,
    request: HTMXRequest,
    id: int,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    task_edit = commands.update_task(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        id=id,
        title=data["title"],
        content=data["content"],
        priority_id=data["priority"],
        deadline=(
            datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M").date()
            if data["deadline"] != ""
            else None
        ),
        status_id=data["status"],
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


@post(
    path="/assign/{project_id:int}/{user_id:str}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def assign_task(
    session: Session,
    request: HTMXRequest,
    project_id: int,
    user_id: str,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Retarget:
    try:
        task_edit = commands.assign_task_project_user(
            session=session,
            user_id=user_id,
            project_id=project_id,
            task_id=int(data["task"]),
        )
        if task_edit == "Success":
            return ClientRedirect(
                redirect_to="/src/users.html",
            )
    except exc.SQLAlchemyError:
        return Retarget(
            content="<span id='error'>Duplicate error</span>",
            target="#another-div",
        )

    except Exception as e:
        return Retarget(
            content=f"<span id='error'>{e}</span>",
            target="#another-div",
        )


hypermedia_tasks_router = Router(
    path="/hypermedia/tasks",
    route_handlers=[
        get_tasks,
        create_task,
        delete_task,
        get_task_edit_form,
        update_task,
        get_tasks_projects,
        get_assign_tasks,
        assign_task,
        get_subtasks_by_task,
    ],
    tags=[
        "Tasks",
    ],
)
