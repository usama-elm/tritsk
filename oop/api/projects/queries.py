from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from api.tables import project_user_rel, projects


def get_projects(
    session: Session,
    user_id: str,
    ids: list[int] | None,
    role: list[str],
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(
            project_user_rel,
            projects.c.id == project_user_rel.c.project_id,
        )
        .where(
            and_(
                project_user_rel.c.user_id == user_id,
                project_user_rel.c.role.in_(role),
            )
        )
    )
    if ids:
        stmt.where(projects.c.id.in_(ids))

    projects_dict = [
        {
            "id": row[projects.c.id],
            "name": row[projects.c.name],
            "description": row[projects.c.description],
        }
        for row in session.execute(stmt).mappings()
    ]
    return projects_dict


def get_projects_by_role(
    session: Session,
    user_id: str,
    role: list[str],
    ids: list[int] | None,
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(
            project_user_rel,
            projects.c.id == project_user_rel.c.project_id,
        )
        .where(
            and_(
                project_user_rel.c.user_id == user_id,
                project_user_rel.c.role.in_(role),
            )
        )
    )
    if ids:
        stmt.where(projects.c.id.in_(ids))

    projects_dict = [
        {
            "id": row[projects.c.id],
            "name": row[projects.c.name],
            "description": row[projects.c.description],
        }
        for row in session.execute(stmt).mappings()
    ]
    return projects_dict


def get_project_by_id(
    session: Session,
    user_id: str,
    id: int,
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(
            project_user_rel,
            projects.c.id == project_user_rel.c.project_id,
        )
        .where(project_user_rel.c.user_id == user_id)
    ).where(projects.c.id == id)

    projects_dict = [
        {
            "id": row[projects.c.id],
            "name": row[projects.c.name],
            "description": row[projects.c.description],
        }
        for row in session.execute(stmt).mappings()
    ]
    return projects_dict
