import asyncio
import datetime
from io import StringIO
from itertools import chain
from logging import getLogger
from typing import Any, Union, cast

from fastapi import APIRouter, Depends, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from pytz import timezone

from src.utils.constants import WEEK_TYPES, EducationForms, Faculties
from src.utils.fake_ua_client import get_http_session
from src.utils.key_builder import ignore_session_key_builder
from src.utils.schedules import get_schedule_with_dates, ua

logger = getLogger("uvicorn.error")
router = APIRouter()


@router.get("/{faculty_id}/{education_form}/")
@cache(key_builder=ignore_session_key_builder)
async def get_groups_list(faculty_id: Faculties, education_form_id: EducationForms, session = Depends(get_http_session)):
    """Get list of groups by their faculty and education form

    - **faculty_id**: faculty id. See `constants.py`
    - **education_form_id**: education form id. See `constants.py`
    """

    query = f"http://schedule.mslu.by/backend/buttonClicked?facultyId={faculty_id}&educationForm={education_form_id}"
    logger.debug(query)

    async with session.get(query, headers={"User-Agent": ua.random}) as resp:
        status_code = resp.status
        body = await resp.json()

        return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


@router.get("/{group_id}/uni_lessons.ics")
@cache(key_builder=ignore_session_key_builder)
async def get_ical_for_group(group_id: int, title_prefix: Union[str, None] = None, session = Depends(get_http_session)):
    """Get schedule for a group by its ID
    
    - **group_id**: group ID
    - **title_prefix**: prefix for calendar events titles. Can contain emoji, e.g. "🎒 ".
    Don't forget the space in order to separate your emoji and the rest of the title
    """

    tasks = []

    for week_type in WEEK_TYPES:
        tasks.append(
            get_schedule_with_dates(
                f"http://schedule.mslu.by/backend/?groupId={group_id}&weekType={week_type}",
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

    for lesson in lessons:
        calendar.events.append(
            Event(
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
                description="Преподаватель: " + lesson["FIO_teacher"],
            )
        )

    calendar_text = StringIO()
    calendar_text.write(IcsCalendarStream.calendar_to_ics(calendar))
    calendar_text = calendar_text.getvalue()

    return Response(content=calendar_text, media_type="text/calendar")