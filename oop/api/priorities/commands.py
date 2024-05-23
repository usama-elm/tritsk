from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import priority


def create_priority(
    session: Session,
    user_id: str,
    title: str,
    rank: str,
    description: int | None = None,
) -> int:
    try:
        if not user_id:
            raise HTTPException(
                detail="Not logged in",
                status_code=400,
            )
        values = {
            "title": title,
            "rank": rank,
        }
        if description:
            values["description"] = description

        stmt = insert(priority).values(**values)
        task = session.execute(stmt)
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


def update_priority(
    session: Session,
    user_id: str,
    priority_id: int,
    title: str | None = None,
    rank: str | None = None,
    description: int | None = None,
) -> int:
    values: dict = {}
    if title:
        values["title"] = title
    if rank:
        values["rank"] = rank
    if description:
        values["description"] = description
    if not values:
        raise ValueError("No information given for an update")
    if not user_id:
        raise HTTPException(
            detail="Not logged in",
            status_code=400,
        )
    try:
        stmt = (
            update(priority).where(and_(priority.c.id == priority_id)).values(**values)
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Priority does not correspond to your user",
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


def delete_priority(
    session: Session,
    user_id: str,
    priority_id: int,
) -> None:
    try:
        if not user_id:
            raise HTTPException(
                detail="Not logged in",
                status_code=400,
            )
        stmt = delete(priority).where(and_(priority.c.priority_id == priority_id))
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Priority does not correspond to your user",
                status_code=400,
            )
        session.commit()
    except Exception as ex:
        raise HTTPException(
            detail=f"Invalid information: {ex}",
            status_code=400,
        )
