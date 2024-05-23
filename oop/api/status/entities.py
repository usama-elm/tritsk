from dataclasses import dataclass

from sqlalchemy.orm import Mapped


@dataclass
class Status:
    id: Mapped[int]
    title: Mapped[str]
