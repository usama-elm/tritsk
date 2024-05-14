from typing import Any

from litestar.exceptions import HTTPException
from sqlalchemy import Row
from sqlalchemy.orm import Session
from toolz import curry

from api.auth.auth import jwt_auth
from api.utils import check_password, fetch_user


@curry
def login_user(user: Row[Any]):
    return (
        jwt_auth.login(identifier=str(user.id))
        .headers["Authorization"]
        .replace("Bearer ", "")
    )


@curry
def login(session: Session, username: str, password: str):
    user = fetch_user(session, username)
    password_valid = check_password(user, password) if user else None

    match (user, password_valid):
        case (None, _):
            raise HTTPException(
                detail="User is not valid",
                status_code=400,
            )
        case (_, False):
            raise HTTPException(
                detail="Password is not valid",
                status_code=400,
            )
        case (_, True):
            return login_user(user)
