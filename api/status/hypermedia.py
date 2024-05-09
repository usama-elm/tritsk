from litestar import Router, get
from litestar.contrib.htmx.response import (
    HTMXTemplate,
)
from litestar.di import Provide
from litestar.response import Template
from sqlalchemy.orm import Session

import api.status.queries as queries
from api.database import get_db


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_status(
    session: Session,
) -> Template:
    return HTMXTemplate(
        template_name="status.get.html",
        context={"status_list": queries.get_status(session=session)},
    )


@get(path="/list", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def give_list_slider(
    session: Session,
) -> Template:
    return HTMXTemplate(
        template_name="list.status.get.html",
        context={
            "status_list": queries.get_status(
                session=session,
            )
        },
    )


hypermedia_status_router = Router(
    path="/hypermedia/status",
    route_handlers=[
        get_status,
        give_list_slider,
    ],
    tags=[
        "Hypermedia",
        "Status",
    ],
)
