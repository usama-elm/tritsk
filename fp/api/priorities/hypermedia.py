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

import api.priorities.commands as commands
import api.priorities.queries as queries
from api.database import get_db
from api.priorities.services import execute_template
from api.utils import get_user_id_by_auth_token


@get(
    path="/",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def get_priorities(
    session: Session,
    request: HTMXRequest,
    ids: list[int] | None = None,
) -> Template:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    context = {
        "priorities": queries.get_priorities(
            session=session,
            user_id=user_id,
        )
    }
    return execute_template("priorities.get.html", context)


@post(
    path="/create",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def create_priorities(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    description = data["description"] if data["description"] else None
    task = commands.create_priority(
        session=session,
        user_id=user_id,
        title=data["title"],
        rank=int(data["rank"]),
        description=description,
    )

    match task:
        case int():
            return ClientRedirect(redirect_to="/src/priorities.html")
        case _:
            return Reswap(
                method="innerHTML",
                content='<span id="error">One and/or more elements of the form are incorrect</span>',
            )


@delete(
    path="/{priority_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=200,
)
def delete_priorities(
    session: Session,
    request: HTMXRequest,
    priority_id: int,
) -> ClientRefresh:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    commands.delete_priority(
        session=session,
        user_id=user_id,
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
    context = {"priority_id": priority_id}
    return execute_template("tasks.edit.form.html", context)


@post(path="{id:int}", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def update_priorities(
    session: Session,
    request: HTMXRequest,
    id: int,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    task_edit = commands.update_priority(
        session=session,
        user_id=user_id,
        priority_id=id,
        title=data["title"],
        rank=data["rank"],
        description=data["description"],
    )

    match task_edit:
        case int():
            return ClientRedirect(redirect_to="/src/priorities.html")
        case _:
            return Reswap(
                method="innerHTML",
                content='<span id="error">One and/or more elements of the form are incorrect</span>',
            )


@get(
    path="/list",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def give_list_slider(
    session: Session,
    request: HTMXRequest,
) -> Template:
    user_id = get_user_id_by_auth_token(token=request.cookies["X-AUTH"])
    context = {
        "priorities": queries.get_priorities(
            session=session,
            user_id=user_id,
        )
    }
    return execute_template("list.priorities.get.html", context)


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
