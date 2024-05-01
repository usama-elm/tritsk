from datetime import date

from sqlalchemy import delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import tasks


def create_task(
    session: Session,
    title: str,
    content: str,
    priority_id: int,
    deadline: date | None = None,
) -> int:
    try:
        if deadline:
            stmt = insert(tasks).values(
                title=title,
                content=content,
                priority_id=priority_id,
                deadline=deadline,
            )
        else:
            stmt = insert(tasks).values(
                title=title,
                content=content,
                priority_id=priority_id,
            )
        result = session.execute(stmt)
        session.commit()
        return result.inserted_primary_key[0]
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Failed to execute database operation: {e}") from e


def update_task(
    session: Session,
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
    try:
        stmt = update(tasks).where(tasks.c.id == id).values(**values)
        session.execute(stmt)
        session.commit()
        return id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Failed to execute database operation: {e}") from e


def delete_task(session: Session, id: int) -> int:
    stmt = delete(tasks).where(tasks.c.id == id)
    session.execute(stmt)
    session.commit()
    return id
