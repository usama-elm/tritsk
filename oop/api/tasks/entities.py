from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Mapped


@dataclass
class Task:
    id: Mapped[int]
    title: Mapped[str]
    content: Mapped[str]
    date_creation: Mapped[datetime]
    priority_id: Mapped[int]
    deadline: Mapped[datetime]
    status_id: Mapped[int]


@dataclass
class TaskUser:
    task_id: Mapped[int]
    project_id: Mapped[int]
    user_id: Mapped[int]
