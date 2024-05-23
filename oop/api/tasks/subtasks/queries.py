from typing import Any

from litestar.exceptions import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from api.tables import status, subtasks, task_user_rel, tasks


def get_subtask_by_id(
    session: Session,
    user_id: str,
    subtask_id: int,
) -> dict[str, Any] | None:
    stmt = (
        select(subtasks)
        .join(
            task_user_rel,
            subtasks.c.task_id == task_user_rel.c.task_id,
        )
        .join(
            status,
            subtasks.c.status_id == status.c.id,
        )
        .where(
            and_(
                subtasks.c.id == subtask_id,
                task_user_rel.c.user_id == user_id,
            )
        )
    )

    task = session.execute(stmt).fetchone()
    if task is None:
        raise HTTPException(
            detail="Task does not correspond to your user",
            status_code=400,
        )
    task_dict = {
        "subtask_id": subtasks.t.id,
        "task_id": subtasks.t.task_id,
        "title": subtasks.t.title,
        "content": subtasks.t.content,
        "date_creation": subtasks.t.date_creation.strftime("%d/%m/%YT%H:%M:%SZ%z"),
        "status_id": status.t.title,
    }
    return task_dict


def get_subtasks_by_task(
    session: Session,
    user_id: str,
    task_id: int,
    ids: list[int] | None = None,
    status_id: int | None = None,
) -> list[dict[str, Any] | None]:
    stmt = (
        select(subtasks, status.c.title)
        .join(
            task_user_rel,
            subtasks.c.task_id == task_user_rel.c.task_id,
        )
        .join(
            status,
            subtasks.c.status_id == status.c.id,
        )
        .where(task_user_rel.c.user_id == user_id)
        .where(subtasks.c.task_id == task_id)
    )

    if ids is not None:
        stmt = stmt.where(tasks.c.id._in(ids))
    if status_id is not None:
        stmt = stmt.where(tasks.c.status_id == status_id)

    tasks_dict = [
        {
            "subtask_id": row[subtasks.c.id],
            "task_id": row[subtasks.c.task_id],
            "title": row[subtasks.c.title],
            "content": row[subtasks.c.content],
            "date_creation": row[subtasks.c.date_creation].strftime(
                "%d/%m/%YT%H:%M:%SZ%z"
            ),
            "status": row[status.c.title],
        }
        for row in session.execute(stmt).mappings()
    ]
    return tasks_dict
