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

import api.priorities.commands as commands
import api.priorities.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_priorities(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="priorities.get.html",
        context={
            "priorities": queries.get_priorities(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
            )
        },
    )


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_priorities(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    task = commands.create_priority(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        title=data["title"],
        rank=int(data["rank"]),
        description=data["description"] if data["description"] else None,
    )
    if isinstance(task, int):
        return ClientRedirect(
            redirect_to="/src/priorities.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">One and/or more elements of the form are incorrect</span>',
        )


@delete(
    path="{priority_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=200,
)
def delete_priorities(
    session: Session,
    request: HTMXRequest,
    priority_id: int,
) -> ClientRefresh:
    commands.delete_priority(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        priority_id=priority_id,
    )
    return ClientRefresh()


@get(
    path="/form/{priority_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_priority_edit_form(
    request: HTMXRequest,
    priority_id: int,
) -> Template:
    return HTMXTemplate(
        template_name="tasks.edit.form.html",
        context={"priority_id": priority_id},
    )


@post(path="{id:int}", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def update_priorities(
    session: Session,
    request: HTMXRequest,
    id: int,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    task_edit = commands.update_priority(
        session=session,
        user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
        id=id,
        title=data["title"],
        rank=data["rank"],
        description=data["description"],
    )
    if isinstance(task_edit, int):
        return ClientRedirect(
            redirect_to="/src/priorities.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">One and/or more elements of the form are incorrect</span>',
        )


@get(path="/list", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def give_list_slider(
    session: Session,
    request: HTMXRequest,
) -> Template:
    return HTMXTemplate(
        template_name="list.priorities.get.html",
        context={
            "priorities": queries.get_priorities(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
            )
        },
    )


hypermedia_priorities_router = Router(
    path="/hypermedia/priorities",
    route_handlers=[
        get_priorities,
        create_priorities,
        update_priorities,
        delete_priorities,
        get_priority_edit_form,
        give_list_slider,
    ],
    tags=[
        "Priorities",
    ],
)
