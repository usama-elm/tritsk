from litestar import Request, Response, Router, delete, patch, post
from litestar.di import Provide
from sqlalchemy.orm import Session

import api.projects.commands as commands
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_project(
    session: Session,
    request: Request,
    name: str,
    description: str | None = None,
) -> Response:

    return Response(
        content={
            "id": commands.create_project(
                session=session,
                name=name,
                description=description,
                user_id=get_user_id_by_auth_token(
                    token=request.headers.dict()["authorization"][0]
                ),
            )
        },
        status_code=201,
    )


@patch(
    path="{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def update_project(
    session: Session,
    request: Request,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
) -> Response:

    return Response(
        content={
            "message": commands.update_project(
                session=session,
                name=name,
                description=description,
                project_id=project_id,
                user_id=get_user_id_by_auth_token(
                    token=request.headers.dict()["authorization"][0]
                ),
            )
        },
        status_code=201,
    )


@delete(
    path="{project_id:int}",
    dependencies={"session": Provide(get_db, sync_to_thread=False)},
)
def delete_project(
    session: Session,
    request: Request,
    project_id: int,
) -> None:
    commands.delete_project(
        session=session,
        project_id=project_id,
        user_id=get_user_id_by_auth_token(
            token=request.headers.dict()["authorization"][0]
        ),
    )


project_router = Router(
    path="/projects",
    route_handlers=[
        create_project,
        update_project,
        delete_project,
    ],
    tags=["Projects"],
)
