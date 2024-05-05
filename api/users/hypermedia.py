from uuid import UUID

from litestar import Router, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import ClientRedirect, Reswap
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from sqlalchemy.orm import Session

import api.users.commands as commands
from api.database import get_db


@post(path="/create", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def create_user(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap:
    user = commands.create_user(
        session=session,
        username=data["username"],
        name=data["name"],
        aftername=data["aftername"],
        mail=data["mail"],
        password=data["password"],
    )
    if isinstance(user, UUID):
        return ClientRedirect(
            redirect_to="/src/login.html",
        )
    else:
        return Reswap(
            method="innerHTML",
            content='<span id="error">User and/or password is incorrect</span>',
        )


hypermedia_users_router = Router(
    path="/hypermedia/users",
    route_handlers=[
        create_user,
    ],
    tags=[
        "Hypermedia",
        "Auth",
    ],
)
