from pathlib import Path

from litestar import Litestar
from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.openapi.config import OpenAPIConfig
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

from api.auth.auth import jwt_auth
from api.auth.hypermedia import hypermedia_auth_router
from api.auth.router import auth_router
from api.projects.hypermedia import hypermedia_projects_router
from api.projects.router import project_router
from api.tasks.hypermedia import hypermedia_tasks_router
from api.tasks.router import task_router
from api.users.hypermedia import hypermedia_users_router
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
        hypermedia_tasks_router,
        hypermedia_auth_router,
        hypermedia_users_router,
        hypermedia_projects_router,
        create_static_files_router(
            path="/src",
            directories=["src"],
        ),
    ],
    on_app_init=[jwt_auth.on_app_init],
    openapi_config=openapi_config,
    cors_config=CORSConfig(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    ),
    allowed_hosts=AllowedHostsConfig(allowed_hosts=["*"]),
    template_config=TemplateConfig(
        directory=Path("api/templates"),
        engine=JinjaTemplateEngine,
    ),
)
