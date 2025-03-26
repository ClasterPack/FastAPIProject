from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str = None



class Film(BaseModel):
    id: str
    title: str = None
    description: Optional[str] = None