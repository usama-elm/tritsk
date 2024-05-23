from dataclasses import dataclass

from sqlalchemy.orm import Mapped


@dataclass
class User:
    id: Mapped[int]
    username: Mapped[str]
    name: Mapped[str]
    aftername: Mapped[str]
    mail: Mapped[str]
    password: Mapped[str]
