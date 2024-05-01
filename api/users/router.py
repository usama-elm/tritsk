from litestar import Response, Router, delete, get, patch, post, put
from litestar.di import Provide
from sqlalchemy.orm import Session

import api.users.commands as commands
import api.users.queries as queries
from api.database import get_db


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


user_router = Router(
    path="/users",
    route_handlers=[create_user],
)
