from typing import Any

from litestar.exceptions import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import api.projects.queries as queries_project
from api.tables import project_user_rel, users


def get_users_by_project(
    session: Session,
    user_id: str,
    project_id: int,
    role: list[str],
) -> list[dict[str, Any] | None]:
    try:
        stmt_chief = (
            select(users.c.id)
            .join(
                project_user_rel,
                users.c.id == project_user_rel.c.user_id,
            )
            .where(
                and_(
                    project_user_rel.c.user_id == user_id,
                    project_user_rel.c.project_id == project_id,
                    project_user_rel.c.role.in_(role),
                )
            )
        )
        id_chief = session.execute(stmt_chief).scalar_one_or_none()
        if id_chief:
            stmt = (
                select(users)
                .join(
                    project_user_rel,
                    users.c.id == project_user_rel.c.user_id,
                )
                .where(
                    and_(
                        project_user_rel.c.user_id != user_id,
                        project_user_rel.c.project_id == project_id,
                    )
                )
            )
        projects_dict = [
            {
                "id": row[users.c.id],
                "username": row[users.c.username],
                "name": row[users.c.name],
                "aftername": row[users.c.aftername],
            }
            for row in session.execute(stmt).mappings()
        ]
        return projects_dict
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            detail="Invalid information",
            status_code=400,
        )


def get_users(
    session: Session,
    user_id: str,
    ids: list[int] | None = None,
) -> list[dict[str, Any] | None]:
    try:
        stmt = select(users).where(users.c.id != user_id)

        projects_dict = [
            {
                "id": row[users.c.id],
                "username": row[users.c.username],
                "name": row[users.c.name],
                "aftername": row[users.c.aftername],
            }
            for row in session.execute(stmt).mappings()
        ]
        return projects_dict
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            detail="Invalid information",
            status_code=400,
        )


def get_all_users(
    session: Session,
    user_id: int,
) -> list[dict[str, dict] | None]:
    projects = queries_project.get_projects(
        session=session,
        user_id=user_id,
        ids=None,
        role=[
            "chief",
            "collaborator",
            "user",
        ],
    )
    tasks_by_projects = []
    for project in projects:
        tasks_by_projects.append(
            {
                "project": project,
                "users": get_users_by_project(
                    session=session,
                    user_id=user_id,
                    project_id=project["id"],
                    role=[
                        "chief",
                        "collaborator",
                        "user",
                    ],
                ),
            }
        )
    return tasks_by_projects
