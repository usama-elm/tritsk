from typing import Any

from litestar import Request, Response, Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.security.jwt import Token
from sqlalchemy.orm import Session

import api.auth.commands as commands
from api.database import get_db
from api.utils import get_user_by_auth_token


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def login(
    username: str,
    password: str,
    session: Session,
) -> Response[dict[str, str]]:
    token_str = commands.login(
        session=session,
        username=username,
        password=password,
    )
    reponse = Response(
        content={"token": token_str},
        status_code=200,
    )
    reponse.set_cookie("X-AUTH", token_str)
    return reponse


@get(path="/current", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_user_by_token(
    session: Session,
    request: Request[Any, Token, Any],
) -> Any:
    try:
        return get_user_by_auth_token(
            token=request.cookies["X-AUTH"],
            session=session,
        )
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
        )


auth_router = Router(
    path="/login",
    route_handlers=[
        login,
        get_user_by_token,
    ],
    tags=["Auth"],
)
