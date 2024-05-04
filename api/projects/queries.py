from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.tables import project_user_rel, projects


def get_tasks(
    session: Session,
    user_id: str,
    ids: list[int] | None,
) -> list[dict[str, Any] | None]:
    stmt = (
        select(projects)
        .join(
            project_user_rel,
            projects.c.id == project_user_rel.c.project_id,
        )
        .where(project_user_rel.c.user_id == user_id)
    )
    if ids:
        stmt.where(projects.c.id._in(ids))

    projects_dict = [
        {
            "id": row[projects.c.id],
            "name": row[projects.c.name],
            "description": row[projects.c.description],
        }
        for row in session.execute(stmt).mappings()
    ]
    return projects_dict
