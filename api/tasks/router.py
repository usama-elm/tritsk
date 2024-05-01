from datetime import datetime

from litestar import Request, Response, Router, delete, get, patch, post
from litestar.di import Provide
from sqlalchemy.orm import Session

import api.tasks.commands as commands
import api.tasks.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="{id:int}", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_task_by_id(
    session: Session,
    request: Request,
    id: int,
) -> Response:
    return Response(
        content=queries.get_task_by_id(
            id=id,
            session=session,
            user_id=get_user_id_by_auth_token(
                token=request.headers.dict()["authorization"][0]
            ),
        ),
        status_code=200,
    )


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_tasks(
    session: Session,
    request: Request,
    ids: list[int] | None = None,
) -> Response:
    return Response(
        content=queries.get_tasks(
            ids=ids,
            session=session,
            user_id=get_user_id_by_auth_token(
                token=request.headers.dict()["authorization"][0]
            ),
        ),
        status_code=200,
    )


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_task(
    session: Session,
    request: Request,
    title: str,
    content: str,
    priority_id: int,
    deadline: str | None = None,
) -> Response:
    return Response(
        content={
            "id": commands.create_task(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.headers.dict()["authorization"][0]
                ),
                title=title,
                content=content,
                priority_id=priority_id,
                deadline=(
                    datetime.strptime(deadline, "%d/%m/%Y").date()
                    if deadline is not None
                    else None
                ),
            )
        },
        status_code=201,
    )


@patch(path="{id:int}", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def update_task(
    session: Session,
    request: Request,
    id: int,
    title: str | None = None,
    content: str | None = None,
    priority_id: int | None = None,
    deadline: str | None = None,
) -> Response:

    return Response(
        content={
            "id": commands.update_task(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.headers.dict()["authorization"][0]
                ),
                id=id,
                title=title,
                content=content,
                priority_id=priority_id,
                deadline=(
                    datetime.strptime(deadline, "%d/%m/%Y").date()
                    if deadline is not None
                    else None
                ),
            )
        },
        status_code=200,
    )


## TODO: Assign task to project


@delete(
    path="{id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
    status_code=204,
)
def delete_task(
    session: Session,
    request: Request,
    id: int,
) -> None:
    commands.delete_task(
        session=session,
        user_id=get_user_id_by_auth_token(
            token=request.headers.dict()["authorization"][0]
        ),
        id=id,
    )


task_router = Router(
    path="/tasks",
    route_handlers=[
        create_task,
        get_tasks,
        get_task_by_id,
        update_task,
        delete_task,
    ],
    tags=["Tasks"],
)
