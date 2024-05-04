from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import project_user_rel, projects


def create_project(
    session: Session,
    user_id: str,
    name: str,
    description: str | None = None,
) -> int:
    try:
        if not user_id:
            raise HTTPException(
                detail="Not logged in",
                status_code=400,
            )
        stmt = insert(projects).values(
            name=name,
            description=description,
        )
        project = session.execute(stmt)
        session.flush()
        stmt_rel = insert(project_user_rel).values(
            project_id=project.inserted_primary_key[0],
            user_id=user_id,
        )

        session.execute(stmt_rel)
        session.commit()
        return project.inserted_primary_key[0]
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


def update_project(
    session: Session,
    user_id: str,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
) -> str:
    values: dict = {}
    if name:
        values["name"] = name
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
            update(projects)
            .where(
                and_(
                    projects.c.id == project_id,
                    projects.c.id == project_user_rel.c.project_id,
                    project_user_rel.c.user_id == user_id,
                )
            )
            .values(**values)
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                detail="Project does not correspond to your user",
                status_code=400,
            )
        session.commit()
        return "Success"
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


def delete_project(session: Session, user_id: str, project_id: int) -> None:
    stmt = delete(projects).where(
        and_(
            projects.c.id == project_id,
            projects.c.id == project_user_rel.c.project_id,
            project_user_rel.c.user_id == user_id,
        )
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            detail="Project does not correspond to your user",
            status_code=400,
        )
    session.commit()
