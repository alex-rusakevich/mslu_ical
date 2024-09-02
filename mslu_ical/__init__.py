import asyncio
import datetime
from io import StringIO
from itertools import chain
from logging import getLogger

import aiohttp
from fake_useragent import UserAgent
from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from pytz import timezone

logger = getLogger("uvicorn.error")
ua = UserAgent()
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

        async with session.get(query, headers={"User-Agent": ua.random}) as resp:
            status_code = resp.status
            body = await resp.json()

            return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


@app.get("/api/ical/{group_id}/uni_lessons.ics")
async def get_ical_for_group(group_id: int):
    async def get_url_data(url, session, week_type: str):
        r = await session.request(
            "GET", url=f"{url}", headers={"User-Agent": ua.random}
        )

        data = await r.json()

        week_first_day = datetime.datetime.today() - datetime.timedelta(
            days=datetime.datetime.today().weekday() % 7
        )

        if week_type.startswith("current"):
            ...
        elif week_type.startswith("next"):
            week_first_day += datetime.timedelta(days=7)
        elif week_type.startswith("third"):
            week_first_day += datetime.timedelta(days=7 * 2)
        elif week_type.startswith("fourth"):
            week_first_day += datetime.timedelta(days=7 * 3)

        data = data["data"]

        for i, _ in enumerate(data):
            data[i]["lessonDay"] = (
                week_first_day + datetime.timedelta(days=(data[i]["DayNumber"] - 1))
            ).strftime("%Y-%d-%m")

        return data

    async with aiohttp.ClientSession() as session:
        tasks = []

        for week_type in WEEK_TYPES:
            tasks.append(
                get_url_data(
                    f"http://schedule.mslu.by/backend/?groupId={group_id}&weekType={week_type}",
                    session=session,
                    week_type=week_type,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

    lessons = list(chain(*results))
    calendar = Calendar()
    bel_tz = timezone("Europe/Minsk")

    for lesson in lessons:
        calendar.events.append(
            Event(
                summary=lesson["Discipline"] + f" ({lesson['Discipline_Type']})",
                start=bel_tz.localize(
                    datetime.datetime.strptime(
                        lesson["lessonDay"]
                        + " "
                        + lesson["TimeIn"].replace(":00.0000000", ""),
                        "%Y-%d-%m %H:%M",
                    )
                ),
                end=bel_tz.localize(
                    datetime.datetime.strptime(
                        lesson["lessonDay"]
                        + " "
                        + lesson["TimeOut"].replace(":00.0000000", ""),
                        "%Y-%d-%m %H:%M",
                    )
                ),
                location=lesson["Classroom"],
                description="Преподаватель: " + lesson["FIO_teacher"],
            )
        )

    calendar_text = StringIO()
    calendar_text.write(IcsCalendarStream.calendar_to_ics(calendar))
    calendar_text = calendar_text.getvalue()

    return Response(content=calendar_text, media_type="text/calendar")
