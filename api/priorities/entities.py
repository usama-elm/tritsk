from dataclasses import dataclass, field

from sqlalchemy.orm import Mapped


@dataclass
class Priority:
    id: Mapped[int] = field(init=False)
    title: Mapped[str]
    rank: Mapped[int]
    description: Mapped[str]
