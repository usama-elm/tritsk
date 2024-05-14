import re
from typing import Any

import litestar.status_codes as status
from jinja2 import Environment, FileSystemLoader, select_autoescape
from litestar.exceptions import HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from toolz import curry

from api.auth.auth import verify_access_token
from api.tables import users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


curried_verify_password = curry(verify_password)


@curry
def check_password(user: Any, password: str):
    match user:
        case None:
            return None
        case _:
            return curried_verify_password(password, user.password)


def fetch_user(session: Session, username: str):
    stmt = select(users).where(users.c.username == username)
    return session.execute(stmt).fetchone()


def check_is_mail(mail: str) -> bool:
    regex_string = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex_string, mail):
        return True
    return False


def get_user_by_auth_token(
    token: str,
    session: Session,
) -> dict[str, str]:
    try:
        token_id: str = verify_access_token(token.replace("Bearer ", ""))
        user_db = session.execute(
            select(users).where(users.c.id == token_id)
        ).fetchone()
        user = {
            "id": user_db.id,
            "username": user_db.username,
            "mail": user_db.mail,
        }
        return user
    except KeyError:
        raise HTTPException(
            detail="User not logged in",
            status_code=400,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_by_auth_token(token: str) -> str:
    try:
        token_id: str = verify_access_token(token.replace("Bearer ", ""))
        return token_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def JinjaEnv():
    return Environment(
        loader=FileSystemLoader("api/templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_template(template_name: str, data: dict, env: Environment):
    template = env.get_template(template_name)
    return template.render(data)
