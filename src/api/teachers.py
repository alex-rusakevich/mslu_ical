import asyncio
import datetime
import json
from io import StringIO
from itertools import chain
from logging import getLogger
from typing import Any, Union, cast

import aiohttp
from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from pytz import timezone

from src.config.settings import settings
from src.network import get_url_data, ua

logger = getLogger("uvicorn.error")
router = APIRouter()


@router.get("/", description="Get the list of all MSLU teachers")
async def get_teachers_list():
    """Get list of MSLU teachers"""
    
    async with aiohttp.ClientSession() as session:
        query = "http://schedule.mslu.by/backend/getTeacherNames"
        logger.debug(query)

        async with session.get(query, headers={"User-Agent": ua.random}) as resp:
            status_code = resp.status
            body = await resp.json()

            return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


@router.get("/{teacher_id}/uni_lessons.ics", description="Get schedule for a teacher by their ID")
async def get_ical_for_teacher(teacher_id: int, title_prefix: Union[str, None] = None):
    """Get schedule for a group by its ID
    
    - **teacher_id**: teacher ID
    - **title_prefix**: prefix for calendar events titles. Can contain emoji, e.g. "🎒 ".
    Don't forget the space in order to separate your emoji and the rest of the title
    """

    async with aiohttp.ClientSession() as session:
        tasks = []

        for week_type in settings.WEEK_TYPES:
            tasks.append(
                get_url_data(
                    f"http://schedule.mslu.by/backend/teachers?teacherId={teacher_id}&weekType={week_type}",
                    session=session,
                    week_type=week_type,
                )
            )

        results: list = await asyncio.gather(*tasks, return_exceptions=True)

    lessons = cast(list[dict[str, Any]], list(chain(*results)))
    calendar = Calendar()
    bel_tz = timezone("Europe/Minsk")

    if not title_prefix:
        title_prefix = ""

    lessons_by_hash = {}

    # Find duplicates
    for lesson in lessons:
        id_obj = {}

        for key in (
            "Discipline",
            "Discipline_Type",
            "lessonDay",
            "TimeIn",
            "TimeOut",
            "Classroom",
        ):
            id_obj[key] = lesson[key]

        unique_repr = hash(json.dumps(id_obj, sort_keys=True))

        lesson["GroupList"] = [lesson["Group"]]

        if lessons_by_hash.get(unique_repr):
            lessons_by_hash[unique_repr]["GroupList"].append(lesson["Group"])
        else:
            lessons_by_hash[unique_repr] = lesson

    lessons = lessons_by_hash.values()

    for lesson in lessons:
        description = ""

        if len(lesson["GroupList"]) > 1:
            description = "Группы: " + ", ".join(lesson["GroupList"])
        else:
            description = "Группа: " + lesson["Group"]

        event = Event(
            summary=title_prefix
            + lesson["Discipline"]
            + f" ({lesson['Discipline_Type']})",
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
            description=description,
        )

        calendar.events.append(event)
    # endregion

    calendar_text = StringIO()
    calendar_text.write(IcsCalendarStream.calendar_to_ics(calendar))
    calendar_text = calendar_text.getvalue()

    return Response(content=calendar_text, media_type="text/calendar")