from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import subtasks, task_user_rel, tasks


def create_subtask(
    session: Session,
    task_id: int,
    user_id: str,
    title: str,
    content: str,
    status_id: int,
) -> int:
    try:
        if not user_id:
            raise HTTPException(
                detail="Not logged in",
                status_code=400,
            )
        values = {
            "title": title,
            "task_id": task_id,
            "content": content,
            "status_id": status_id,
        }

        stmt = insert(subtasks).values(**values)
        task = session.execute(stmt)
        session.flush()
        session.commit()
        return task.inserted_primary_key[0]
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


def update_subtask(
    session: Session,
    user_id: str,
    subtask_id: int,
    title: str | None = None,
    content: str | None = None,
    status_id: int | None = None,
) -> int:
    values: dict = {}
    if title:
        values["title"] = title
    if content:
        values["content"] = content
    if status_id:
        values["status_id"] = status_id
    if not values:
        raise ValueError("No information given for an update")
    if not user_id:
        raise HTTPException(
            detail="Not logged in",
            status_code=400,
        )
    try:
        stmt = (
            update(subtasks)
            .where(
                and_(
                    subtasks.c.id == subtask_id,
                    subtasks.c.task_id == task_user_rel.c.task_id,
                    task_user_rel.c.user_id == user_id,
                )
            )
            .values(**values)
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Subtask does not correspond to your user",
                status_code=400,
            )
        session.commit()
        return subtask_id
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception as ex:
        raise HTTPException(
            detail=f"Invalid information: {ex}",
            status_code=400,
        )


def delete_subtask(
    session: Session,
    user_id: str,
    subtask_id: int,
) -> None:
    stmt = delete(tasks).where(
        and_(
            subtasks.c.id == subtask_id,
            subtasks.c.task_id == task_user_rel.c.task_id,
            task_user_rel.c.user_id == user_id,
        )
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            detail="Subtask does not correspond to your user",
            status_code=400,
        )
    session.commit()
