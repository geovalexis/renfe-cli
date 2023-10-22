from pydantic import BaseModel


class Station(BaseModel):
    name: str
    id: str


class Timetable(BaseModel):
    type: str
    departure: str
    arrival: str
    duration: str
    prices: list[str]
