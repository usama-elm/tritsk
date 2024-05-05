from datetime import datetime

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

import api.tasks.commands as commands
import api.tasks.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_tasks(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
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
    )
    if isinstance(task, int):
        return ClientRedirect(
            redirect_to="/src/main.html",
        )
    else:
        return Reswap(
            method="innerHTML",
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


hypermedia_tasks_router = Router(
    path="/hypermedia/tasks",
    route_handlers=[
        get_tasks,
        create_task,
        delete_task,
        get_task_edit_form,
        update_task,
    ],
    tags=[
        "Hypermedia",
        "Tasks",
    ],
)
