from datetime import date

from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import project_user_rel, task_user_rel, tasks


def create_task(
    session: Session,
    user_id: str,
    title: str,
    content: str,
    priority_id: int,
    project_id: int,
    deadline: date | None = None,
) -> int:
    try:
        if not user_id:
            raise HTTPException(
                detail="Not logged in",
                status_code=400,
            )
        values = {"title": title, "content": content, "priority_id": priority_id}
        if deadline:
            values["deadline"] = deadline
        stmt = insert(tasks).values(**values)
        task = session.execute(stmt)
        session.flush()
        task_project = assign_task_project_user(
            session=session,
            user_id=user_id,
            task_id=task.inserted_primary_key[0],
            project_id=int(project_id),
        )
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


def update_task(
    session: Session,
    user_id: str,
    id: int,
    title: str | None = None,
    content: str | None = None,
    priority_id: int | None = None,
    deadline: date | None = None,
) -> int:
    values: dict = {}
    if title:
        values["title"] = title
    if content:
        values["content"] = content
    if priority_id:
        values["priority_id"] = priority_id
    if deadline:
        values["deadline"] = deadline
    if not values:
        raise ValueError("No information given for an update")
    if not user_id:
        raise HTTPException(
            detail="Not logged in",
            status_code=400,
        )
    try:
        stmt = (
            update(tasks)
            .where(
                and_(
                    tasks.c.id == id,
                    tasks.c.id == task_user_rel.c.task_id,
                    task_user_rel.c.user_id == user_id,
                )
            )
            .values(**values)
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Task does not correspond to your user",
                status_code=400,
            )
        session.commit()
        return id
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


def delete_task(
    session: Session,
    user_id: str,
    id: int,
) -> None:
    stmt = delete(tasks).where(
        and_(
            tasks.c.id == id,
            tasks.c.id == task_user_rel.c.task_id,
            task_user_rel.c.user_id == user_id,
        )
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            detail="Project does not correspond to your user",
            status_code=400,
        )
    session.commit()


def assign_task_project_user(
    session: Session,
    user_id: str,
    task_id: int,
    project_id: int,
) -> str | HTTPException:
    stmt_conf = (
        select(project_user_rel.c.user_id)
        .where(
            project_user_rel.c.user_id == user_id,
        )
        .where(
            project_user_rel.c.project_id == project_id,
        )
        .where(
            or_(
                project_user_rel.c.role == "chief",
                project_user_rel.c.role == "collaborator",
            )
        )
    )

    if session.execute(stmt_conf).scalar_one_or_none():
        stmt = insert(task_user_rel).values(
            task_id=task_id,
            user_id=user_id,
            project_id=project_id,
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Task does not correspond to your user",
                status_code=400,
            )
        session.commit()
        return "Success"
    else:
        raise HTTPException(
            detail="User doesn't have the rights",
            status_code=400,
        )
