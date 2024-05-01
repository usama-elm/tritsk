from litestar import Litestar
from litestar.openapi.config import OpenAPIConfig

from api.auth.auth import jwt_auth
from api.auth.router import auth_router
from api.projects.router import project_router
from api.tasks.router import task_router
from api.users.router import user_router

openapi_config = OpenAPIConfig(
    title="TriTsk",
    version="1.0.0",
)

app = Litestar(
    route_handlers=[
        auth_router,
        task_router,
        user_router,
        project_router,
    ],
    on_app_init=[jwt_auth.on_app_init],
    openapi_config=openapi_config,
)
