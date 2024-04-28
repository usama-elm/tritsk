from litestar import Litestar

from api.tasks.router import task_router

app = Litestar(route_handlers=[task_router])
