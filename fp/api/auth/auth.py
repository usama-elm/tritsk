from typing import Any

import litestar.status_codes as status
from jose import JWTError, jwt
from litestar.exceptions import HTTPException
from litestar.security.jwt import JWTCookieAuth, Token
from sqlalchemy import Row, select
from sqlalchemy.orm import Session
from toolz import curry

from api.config import ALGORITHM, JWT_SECRET
from api.tables import users


@curry
def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


@curry
def get_id_from_payload(payload: dict[str, Any]) -> str:
    return payload.get("sub") if payload else None


@curry
def verify_access_token(
    token,
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED
    ),
):
    payload = decode_token(token)
    id = get_id_from_payload(payload)

    match id:
        case None:
            raise credentials_exception
        case _:
            return id


def get_current_user(token: Token, session: Session) -> Row[Any] | None:
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_id: str = verify_access_token(token, credentials_exception)
    user = session.execute(select(users).where(users.c.id == token_id)).fetchone()
    return user


jwt_auth = JWTCookieAuth[Row[Any]](
    retrieve_user_handler=get_current_user,
    token_secret=JWT_SECRET,
    algorithm=ALGORITHM,
    exclude=[
        "/login",
        "/schema",
        "/users",
        "/projects",
        "/tasks",
        "/hypermedia",
        "/src",
    ],
)
