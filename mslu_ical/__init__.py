import asyncio
import datetime
from io import StringIO
from itertools import chain
from logging import getLogger

import aiohttp
from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event

logger = getLogger("uvicorn.error")
app = FastAPI()


FACULTY_IDS = {
    "ФКЯиК": 221,
    "ФАЯ": 202,
    "ФНЯ": 196,
    "ФРЯ": 222,
    "ПФ": 203,
    "ФМК": 193,
    "Магистратура": 217,
}

WEEK_TYPES = ["currentWeek", "nextWeek", "thirdWeek", "fourthWeek"]

EDUCATION_FORMS = {"Очная": 1, "Заочная": 2}


@app.get("/api/groups/{faculty_id}/{education_form}/")
async def get_groups_list(faculty_id: int, education_form: int):
    async with aiohttp.ClientSession() as session:
        query = f"http://schedule.mslu.by/backend/buttonClicked?facultyId={faculty_id}&educationForm={education_form}"
        logger.debug(query)

        async with session.get(query) as resp:
            status_code = resp.status
            body = await resp.json()

            return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


@app.get("/api/ical/{group_id}/")
async def get_ical_for_group(group_id: int):
    async def get_url_data(url, session):
        r = await session.request("GET", url=f"{url}")
        data = await r.json()
        return data["data"]

    async with aiohttp.ClientSession() as session:
        tasks = []

        for week_type in WEEK_TYPES:
            tasks.append(
                get_url_data(
                    f"http://schedule.mslu.by/backend/?groupId={group_id}&weekType={week_type}",
                    session=session,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

    lessons = list(chain(*results))
    calendar = Calendar()

    for lesson in lessons:
        calendar.events.append(
            Event(
                summary=lesson["Discipline"] + f" ({lesson['Discipline_Type']})",
                start=datetime.datetime.strptime(
                    lesson["DateIn"]
                    + " "
                    + lesson["TimeIn"].replace(":00.0000000", ""),
                    "%Y-%m-%d %H:%M",
                ),
                end=datetime.datetime.strptime(
                    lesson["DateOut"]
                    + " "
                    + lesson["TimeOut"].replace(":00.0000000", ""),
                    "%Y-%m-%d %H:%M",
                ),
                location=lesson["Classroom"],
                description="Преподаватель: " + lesson["FIO_teacher"],
            )
        )

    calendar_text = StringIO()
    calendar_text.write(IcsCalendarStream.calendar_to_ics(calendar))

    return Response(content=calendar_text.getvalue(), media_type="text/calendar")