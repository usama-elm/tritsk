from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, update
from sqlalchemy.orm import Session
from toolz import curry

from api.priorities.services import (
    check_user_id,
    create_values_map,
    execute_statement,
    handle_exceptions,
)
from api.tables import priority


# Create priority
@curry
def create_priority(
    session: Session,
    user_id: str,
    title: str,
    rank: str,
    description: int | None = None,
) -> int:
    user_check = check_user_id(user_id)
    values = create_values_map(title, rank, description)

    match (user_check, description):
        case (None, _):
            raise HTTPException(detail="Not logged in", status_code=400)
        case (_, _):
            stmt = insert(priority).values(**values)
            task = handle_exceptions(session, execute_statement, session, stmt)
            return task.inserted_primary_key[0]


# Update priority
@curry
def update_priority(
    session: Session,
    user_id: str,
    priority_id: int,
    title: str | None = None,
    rank: str | None = None,
    description: int | None = None,
) -> int:
    user_check = check_user_id(user_id)
    values = create_values_map(title, rank, description)

    if not values:
        raise ValueError("No information given for an update")

    match user_check:
        case None:
            raise HTTPException(detail="Not logged in", status_code=400)
        case _:
            stmt = (
                update(priority)
                .where(and_(priority.c.id == priority_id))
                .values(**values)
            )
            result = handle_exceptions(session, execute_statement, session, stmt)
            if result.rowcount == 0:
                raise HTTPException(
                    detail="Priority does not correspond to your user", status_code=400
                )
            return priority_id


# Delete priority
@curry
def delete_priority(session: Session, user_id: str, priority_id: int) -> None:
    user_check = check_user_id(user_id)

    match (user_check, priority_id):
        case (None, _):
            raise HTTPException(detail="Not logged in", status_code=400)
        case (_, _):
            stmt = delete(priority).where(and_(priority.c.priority_id == priority_id))
            result = handle_exceptions(session, execute_statement, session, stmt)
            if result.rowcount == 0:
                raise HTTPException(
                    detail="Priority does not correspond to your user", status_code=400
                )
