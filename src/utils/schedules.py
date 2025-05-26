import datetime

from fake_useragent import UserAgent

ua = UserAgent()


async def get_schedule_with_dates(url, session, week_type: str):
    r = await session.request("GET", url=f"{url}", headers={"User-Agent": ua.random})

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