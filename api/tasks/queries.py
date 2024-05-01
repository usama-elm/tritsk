from typing import Any

from litestar.exceptions import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from api.tables import task_user_rel, tasks


def get_task_by_id(
    session: Session,
    user_id: str,
    id: int,
) -> dict[str, Any] | None:
    stmt = (
        select(tasks)
        .join(
            task_user_rel,
            tasks.c.id == task_user_rel.c.task_id,
        )
        .where(
            and_(
                tasks.c.id == id,
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
    print()
    task_dict = {
        "id": task.t.id,
        "title": task.t.title,
        "content": task.t.content,
        "date_creation": task.t.date_creation.strftime("%d/%m/%YT%H:%M:%SZ%z"),
        "priority_id": task.t.priority_id,
        "deadline": (
            task.t.deadline.strftime("%d/%m/%Y")
            if task.t.deadline is not None
            else None
        ),
    }
    return task_dict


def get_tasks(
    session: Session,
    user_id: str,
    ids: list[int] | None,
) -> list[dict[str, Any] | None]:
    stmt = (
        select(tasks)
        .join(
            task_user_rel,
            tasks.c.id == task_user_rel.c.task_id,
        )
        .where(task_user_rel.c.user_id == user_id)
    )
    if ids:
        stmt.where(tasks.c.id._in(ids))

    tasks_dict = [
        {
            "id": row[tasks.c.id],
            "title": row[tasks.c.title],
            "content": row[tasks.c.content],
            "date_creation": row[tasks.c.date_creation].strftime(
                "%d/%m/%YT%H:%M:%SZ%z"
            ),
            "priority_id": row[tasks.c.priority_id],
            "deadline": (
                row[tasks.c.deadline].strftime("%d/%m/%Y")
                if row[tasks.c.deadline] is not None
                else None
            ),
        }
        for row in session.execute(stmt).mappings()
    ]
    return tasks_dict
