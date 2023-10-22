from pydantic import BaseModel


class Station(BaseModel):
    name: str
    id: str
