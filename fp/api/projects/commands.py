from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, update
from sqlalchemy.orm import Session
from toolz import curry

from api.projects.services import check_user_id, execute_statement, handle_exceptions
from api.tables import project_user_rel, projects


# Create project
@curry
def create_project(
    session: Session,
    user_id: str,
    name: str,
    description: str | None = None,
) -> int:
    user_check = check_user_id(user_id)

    match (user_check, description):
        case (None, _):
            raise HTTPException(detail="Not logged in", status_code=400)
        case (_, _):
            stmt = insert(projects).values(name=name, description=description)
            project = handle_exceptions(session, execute_statement, session, stmt)
            session.flush()
            stmt_rel = insert(project_user_rel).values(
                project_id=project.inserted_primary_key[0],
                user_id=user_id,
                role="chief",
            )
            handle_exceptions(session, execute_statement, session, stmt_rel)
            return project.inserted_primary_key[0]


# Update project
@curry
def update_project(
    session: Session,
    user_id: str,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
) -> str:
    user_check = check_user_id(user_id)
    values = {
        key: value
        for key, value in {"name": name, "description": description}.items()
        if value is not None
    }

    if not values:
        raise ValueError("No information given for an update")

    match user_check:
        case None:
            raise HTTPException(detail="Not logged in", status_code=400)
        case _:
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
            result = handle_exceptions(session, execute_statement, session, stmt)
            if result.rowcount == 0:
                raise HTTPException(
                    detail="Project does not correspond to your user", status_code=400
                )
            return "Success"


# Delete project
@curry
def delete_project(
    session: Session,
    user_id: str,
    project_id: int,
) -> None:
    user_check = check_user_id(user_id)

    match (user_check, project_id):
        case (None, _):
            raise HTTPException(detail="Not logged in", status_code=400)
        case (_, _):
            stmt = delete(projects).where(
                and_(
                    projects.c.id == project_id,
                    projects.c.id == project_user_rel.c.project_id,
                    project_user_rel.c.user_id == user_id,
                )
            )
            result = handle_exceptions(session, execute_statement, session, stmt)
            if result.rowcount == 0:
                raise HTTPException(
                    detail="Project does not correspond to your user", status_code=400
                )
