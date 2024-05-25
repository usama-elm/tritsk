from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from toolz import curry

from api.projects.services import execute_query
from api.tables import project_user_rel, projects


# Get projects
@curry
def get_projects(
    session: Session, user_id: str, ids: list[int] | None, role: list[str]
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(project_user_rel, projects.c.id == project_user_rel.c.project_id)
        .where(
            and_(
                project_user_rel.c.user_id == user_id, project_user_rel.c.role.in_(role)
            )
        )
    )

    match ids:
        case None:
            pass
        case _:
            stmt = stmt.where(projects.c.id.in_(ids))

    columns = ["id", "name", "description"]
    return execute_query(session, stmt, columns)


# Get projects by role
@curry
def get_projects_by_role(
    session: Session, user_id: str, role: list[str], ids: list[int] | None
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(project_user_rel, projects.c.id == project_user_rel.c.project_id)
        .where(
            and_(
                project_user_rel.c.user_id == user_id, project_user_rel.c.role.in_(role)
            )
        )
    )

    match ids:
        case None:
            pass
        case _:
            stmt = stmt.where(projects.c.id.in_(ids))

    columns = ["id", "name", "description"]
    return execute_query(session, stmt, columns)


# Get project by id
@curry
def get_project_by_id(
    session: Session, user_id: str, id: int
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(project_user_rel, projects.c.id == project_user_rel.c.project_id)
        .where(and_(project_user_rel.c.user_id == user_id, projects.c.id == id))
    )

    columns = ["id", "name", "description"]
    return execute_query(session, stmt, columns)
