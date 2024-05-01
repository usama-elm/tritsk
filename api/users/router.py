from typing import Any

from litestar import Request, Response, Router, delete, patch, post
from litestar.di import Provide
from litestar.security.jwt import Token
from sqlalchemy.orm import Session

import api.users.commands as commands
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_user(
    session: Session,
    username: str,
    name: str,
    aftername: str,
    mail: str,
    password: str,
) -> Response:
    return Response(
        content={
            "id": commands.create_user(
                session=session,
                username=username,
                name=name,
                aftername=aftername,
                mail=mail,
                password=password,
            )
        },
        status_code=201,
    )


@patch(path="", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def update_user(
    session: Session,
    request: Request[Any, Token, Any],
    username: str | None = None,
    name: str | None = None,
    aftername: str | None = None,
    mail: str | None = None,
) -> Response:
    return Response(
        content={
            "message": commands.update_user(
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.headers.dict()["authorization"][0]
                ),
                username=username,
                name=name,
                aftername=aftername,
                mail=mail,
            )
        },
        status_code=200,
    )


@delete(path="", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def delete_user(
    session: Session,
    request: Request[Any, Token, Any],
    password: str,
) -> None:
    commands.delete_task(
        session=session,
        user_id=get_user_id_by_auth_token(
            token=request.headers.dict()["authorization"][0]
        ),
        password=password,
    ),


user_router = Router(
    path="/users",
    route_handlers=[
        create_user,
        update_user,
        delete_user,
    ],
    tags=["Users"],
)
