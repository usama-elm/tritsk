from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Mapped


@dataclass
class Subatsk:
    id: Mapped[int]
    task_id: Mapped[int]
    title: Mapped[str]
    content: Mapped[str]
    date_creation: Mapped[datetime]
    status_id: Mapped[int]
