from litestar.exceptions import HTTPException
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import project_user_rel, users
from api.utils import check_is_mail, hash_password, verify_password


def create_user(
    session: Session,
    username: str,
    name: str,
    aftername: str | None,
    mail: str,
    password: str,
) -> int:
    try:
        if not check_is_mail(mail):
            raise HTTPException(
                detail="Mail is not valid",
                status_code=400,
            )

        stmt = insert(users).values(
            username=username,
            name=name,
            aftername=aftername,
            mail=mail,
            password=hash_password(password),
        )
        result = session.execute(stmt)
        session.commit()
        return result.inserted_primary_key[0]
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )


def update_user(
    session: Session,
    user_id: str,
    username: str | None = None,
    name: str | None = None,
    aftername: str | None = None,
    mail: str | None = None,
) -> str:
    values: dict = {}
    if username:
        values["username"] = username
    if name:
        values["name"] = name
    if aftername:
        values["aftername"] = aftername
    if mail:
        values["mail"] = mail
    if not values:
        raise ValueError(f"No information given for an update")

    try:
        stmt = update(users).where(users.c.id == user_id).values(**values)
        session.execute(stmt)
        session.commit()
        return "Success"
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            detail=f"Invalid information",
            status_code=400,
        )


def delete_task(
    session: Session,
    user_id: str,
    password: str,
) -> str:
    try:
        stmt = select(users).where(and_(users.c.id == user_id))
        user = session.execute(stmt).fetchone()
        if verify_password(password, user.password):
            session.execute(delete(users).where(users.c.id == user_id))
            session.commit()
            return "User successfully deleted"
    except Exception:
        raise HTTPException(
            detail=f"Not logged in and/or wrong password",
            status_code=400,
        )


def add_role_to_user(
    session: Session,
    user_id: str,
    project_id: int,
    role: str,
) -> str:
    try:
        stmt = (
            update(project_user_rel)
            .where(
                and_(
                    project_user_rel.c.user_id == user_id,
                    project_user_rel.c.project_id == project_id,
                )
            )
            .values(
                role=role,
            )
        )
        session.execute(stmt)
        session.commit()
        return "Success"
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            detail=f"Invalid information",
            status_code=400,
        )


def add_user_to_project(
    session: Session,
    user_id: str,
    project_id: int,
    role: str,
) -> str:
    try:
        stmt = insert(project_user_rel).values(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        session.execute(stmt)
        session.commit()
        return "Success"
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            detail=f"Invalid information",
            status_code=400,
        )


## TODO: Implement a password recovery using mail SMTP module, create a custom mail
