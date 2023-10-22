from typing import List, Union

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from renfe.models import Station, Timetable
from renfe.stations import get_station_and_key, get_station_name
from renfe.stations import get_stations as get_stations_logic
from renfe.stations import station_exists
from renfe.timetable import get_days, get_timetable

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
stations_router = APIRouter(prefix="/stations", tags=["stations"])


@stations_router.get("")
def get_stations() -> List[Station]:
    return get_stations_logic()


@stations_router.get("/{station_name}")
def get_station(station_name: str) -> List[Station]:
    return get_station_and_key(station_name)


app.include_router(stations_router)


## Trains CRUD
trains_router = APIRouter(prefix="/trains", tags=["trains"])


@trains_router.get(
    "",
    responses={
        400: {
            "description": "Invalid origin or destination station!",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid origin station!",
                    }
                }
            },
        },
        505: {
            "description": "Error parsing site",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error parsing site!",
                    }
                }
            },
        },
    },
)
def get_trains(
    origin: str, destination: str, date: str, search_timeout: int = 3
) -> List[Timetable]:
    if not station_exists(origin):
        raise HTTPException(status_code=400, detail="Invalid origin station!")
    if not station_exists(destination):
        raise HTTPException(status_code=400, detail="Invalid destination station!")
    days = get_days(date)
    try:
        timetable = get_timetable(
            origin=get_station_name(origin),
            destination=get_station_name(destination),
            days_from_today=days,
            search_timeout=search_timeout,
        )
        return timetable
    except NoSuchElementException as ex:
        raise HTTPException(
            status_code=505,
            detail="Parsing failed! Something has changed in renfe site: " + str(ex),
        ) from ex
    except WebDriverException as ex:
        raise HTTPException(
            status_code=505,
            detail="Something went wrong while trying to navigate through renfe site: "
            + str(ex),
        ) from ex


app.include_router(trains_router)


def main():
    uvicorn.run(
        app="renfe.api:app",
    )
