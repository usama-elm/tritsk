from litestar import Request, Response, Router, delete, get, patch, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from sqlalchemy.orm import Session

import api.projects.commands as commands
import api.projects.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_projects(
    session: Session,
    request: Request,
    ids: list[int] | None = None,
) -> Response:
    try:
        return Response(
            content=queries.get_tasks(
                ids=ids,
                session=session,
                user_id=get_user_id_by_auth_token(token=request.cookies["X-AUTH"]),
            ),
            status_code=200,
        )
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
        )


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_project(
    session: Session,
    request: Request,
    name: str,
    description: str | None = None,
) -> Response:
    try:
        return Response(
            content={
                "id": commands.create_project(
                    session=session,
                    name=name,
                    description=description,
                    user_id=get_user_id_by_auth_token(
                        token=request.cookies["X-AUTH"],
                    ),
                )
            },
            status_code=201,
        )
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
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
    try:
        return Response(
            content={
                "message": commands.update_project(
                    session=session,
                    name=name,
                    description=description,
                    project_id=project_id,
                    user_id=get_user_id_by_auth_token(
                        token=request.cookies["X-AUTH"],
                    ),
                )
            },
            status_code=201,
        )
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
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
    try:
        commands.delete_project(
            session=session,
            project_id=project_id,
            user_id=get_user_id_by_auth_token(
                token=request.cookies["X-AUTH"],
            ),
        )
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
        )


project_router = Router(
    path="/projects",
    route_handlers=[
        get_projects,
        create_project,
        update_project,
        delete_project,
    ],
    tags=["Projects"],
)
