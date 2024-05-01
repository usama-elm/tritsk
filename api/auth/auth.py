from typing import Any

import litestar.status_codes as status
from jose import JWTError, jwt
from litestar.exceptions import HTTPException
from litestar.security.jwt import JWTAuth, Token
from sqlalchemy import Row, select
from sqlalchemy.orm import Session

from api.tables import users

JWT_SECRET = "56ca36aabb26efa8634eb53db6cf021052b81078f230f8191a13ca01b6c12b1d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = "30"


def verify_access_token(
    token: str,
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED
    ),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
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


jwt_auth = JWTAuth[Row[Any]](
    retrieve_user_handler=get_current_user,
    token_secret=JWT_SECRET,
    algorithm=ALGORITHM,
    exclude=["/login", "/schema", "/users", "/projects"],
)
