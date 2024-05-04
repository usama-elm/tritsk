from litestar import Request, Router, get
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.di import Provide
from litestar.response import Template
from sqlalchemy.orm import Session

import api.tasks.queries as queries
from api.database import get_db
from api.utils import get_user_id_by_auth_token


@get(path="/", dependencies={"session": Provide(get_db, sync_to_thread=False)})
def get_tasks(
    session: Session,
    request: Request,
    ids: list[int] | None = None,
) -> Template:
    return HTMXTemplate(
        template_name="tasks.get.html",
        context={
            "tasks": queries.get_tasks(
                ids=ids,
                session=session,
                user_id=get_user_id_by_auth_token(
                    token=request.cookies["X-AUTH"],
                ),
            )
        },
    )


hypermedia_tasks_router = Router(
    path="/hypermedia/tasks",
    route_handlers=[
        get_tasks,
    ],
    tags=[
        "Hypermedia",
        "Tasks",
    ],
)
