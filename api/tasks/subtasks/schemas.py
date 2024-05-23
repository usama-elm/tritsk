from pydantic import BaseModel


class example(BaseModel):
    id: int
    something: str


# (schemas de création, modification, et get)
