from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateTask:
    title: str
    content: str
    priority_id: int
    # deadline: datetime | None = None
