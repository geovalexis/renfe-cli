from typing import List, Union

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from renfe.models import Station
from renfe.stations import get_station_and_key
from renfe.stations import get_stations as get_stations_logic

app = FastAPI(title="RENFE API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/is-alive")
def is_alive():
    return {"status": "we good!"}


## Stations CRUD
stations_router = APIRouter(prefix="/stations", tags=["Stations"])


@stations_router.get("")
def get_stations() -> List[Station]:
    return get_stations_logic()


@stations_router.get("/{station_name}")
def get_station(station_name: str) -> List[Station]:
    return get_station_and_key(station_name)


app.include_router(stations_router)


def main():
    uvicorn.run(
        app="renfe.api:app",
    )
