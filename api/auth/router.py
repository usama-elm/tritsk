from typing import Any

from litestar import Request, Response, Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.security.jwt import JWTAuth, Token
from sqlalchemy import Row, select
from sqlalchemy.orm import Session
from typing_extensions import Annotated

import api.users.commands as commands
import api.users.queries as queries
from api.auth.auth import jwt_auth
from api.database import get_db
from api.tables import users
from api.utils import get_user_by_auth_token, verify_password


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def login(
    request: Request, username: str, password: str, session: Session
) -> Response[dict[str, str]]:
    stmt = select(users).where(users.c.username == username)
    user = session.execute(stmt).fetchone()
    if user:
        if verify_password(password, user.password):
            le_token = jwt_auth.login(identifier=str(user.id))
            response = Response(
                content={
                    "token": le_token.headers["Authorization"].replace("Bearer ", "")
                },
                status_code=200,
            )
            return le_token
        else:
            raise HTTPException(
                detail="Password is not valid",
                status_code=400,
            )
    else:
        raise HTTPException(
            detail="User is not valid",
            status_code=400,
        )


@get(path="/example", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_user_by_token(
    session: Session,
    request: Request[Any, Token, Any],
) -> Any:
    print()
    return get_user_by_auth_token(
        token=request.headers.dict()["authorization"][0],
        session=session,
    )


auth_router = Router(
    path="/login",
    route_handlers=[login, get_user_by_token],
    tags=["Auth"],
)
