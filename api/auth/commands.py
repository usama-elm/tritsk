from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth.auth import jwt_auth
from api.tables import users
from api.utils import verify_password


def login(session: Session, username: str, password: str):
    stmt = select(users).where(users.c.username == username)
    user = session.execute(stmt).fetchone()
    if user:
        if verify_password(password, user.password):
            return (
                jwt_auth.login(identifier=str(user.id))
                .headers["Authorization"]
                .replace("Bearer ", "")
            )

        else:
            raise HTTPException(
                detail="Password is not valid",
                status_code=400,
            )
    else:
        raise HTTPException(
            detail="User is not valid",
            status_code=400,
        )
