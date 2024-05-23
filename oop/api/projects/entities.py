from dataclasses import dataclass

from sqlalchemy.orm import Mapped


@dataclass
class Project:
    id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]


@dataclass
class ProjectUser:
    id: Mapped[int]
    project_id: Mapped[int]
    user_id: Mapped[int]
    role: Mapped[str]
