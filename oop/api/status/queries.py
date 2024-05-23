from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.tables import status


def get_status(
    session: Session,
) -> list[dict[str, Any]]:
    stmt = select(status)

    status_dict = [
        {
            "id": row[status.c.id],
            "title": row[status.c.title],
        }
        for row in session.execute(stmt).mappings()
    ]
    return status_dict


def get_status_by_name(
    session: Session,
    name: str,
) -> list[dict[str, Any]]:
    stmt = select(status).where(
        status.c.title == name,
    )

    row = session.execute(stmt).mappings()

    return {
        "id": row[status.c.id],
        "title": row[status.c.title],
    }
