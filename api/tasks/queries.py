from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.tables import tasks


def get_task_by_id(
    session: Session,
    id: int,
) -> dict[str, Any] | None:
    stmt = select(tasks).where(tasks.c.id == id)

    task = session.execute(stmt).fetchone()
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
    ids: list[int] | None,
) -> list[dict[str, Any] | None]:
    stmt = select(tasks)
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
