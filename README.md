MSLU ICal
===

MSLU ICal provides API to access Minsk State Linguistics University schedules as
.ical files. This is useful when connecting the schedule to calendar services,
such as Google Calendar.

## Installing and running the server

Requirements: `python>=3.12`, `poetry`, `redis>=5`.

Running dev server:

```bash
poetry install
poetry run poe dev
```

Check the status of the server via curl:

```bash
curl localhost:8080
> {"message":"Welcome to the API","documentation":"/docs","redoc":"/redoc"}
```
