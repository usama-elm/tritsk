from datetime import date, datetime

import litestar.status_codes as status
from litestar.exceptions import HTTPException
from litestar.security.jwt import Token
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.tables import users
from api.utils import check_is_mail, hash_password


def create_user(
    session: Session,
    username: str,
    name: str,
    aftername: str,
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
