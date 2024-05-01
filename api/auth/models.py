from dataclasses import dataclass
from uuid import uuid4


@dataclass
class LoginUser:
    id: uuid4
    username: str
    mail: str
