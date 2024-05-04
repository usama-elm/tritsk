from litestar import Router, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import ClientRedirect, HXLocation, Reswap
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from sqlalchemy.orm import Session

import api.auth.commands as commands
from api.database import get_db


@post(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def login(
    session: Session,
    request: HTMXRequest,
    data: dict = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> ClientRedirect | Reswap | HXLocation:
    try:
        token_str = commands.login(
            session=session,
            username=data["username"],
            password=data["password"],
        )
        response = ClientRedirect(
            redirect_to="/src/main.html",
        )
        response.set_cookie(
            key="X-AUTH",
            value=token_str,
            domain="app-local.loc",
            samesite="lax",
        )
        return response
    except HTTPException:
        return Reswap(
            method="innerHTML",
            content='<span id="error">User and/or password is incorrect</span>',
        )


hypermedia_auth_router = Router(
    path="/hypermedia/login",
    route_handlers=[
        login,
    ],
    tags=[
        "Hypermedia",
        "Auth",
    ],
)
