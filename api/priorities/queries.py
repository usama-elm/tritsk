from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.tables import priority


def get_priorities(
    session: Session,
    user_id: str,
) -> list[dict[str, Any] | None]:
    stmt = select(priority)

    priorities_dict = [
        {
            "id": row[priority.c.id],
            "title": row[priority.c.title],
            "rank": row[priority.c.rank],
            "description": row[priority.c.description],
        }
        for row in session.execute(stmt).mappings()
    ]
    return priorities_dict
