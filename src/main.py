from fastapi import FastAPI

from src.api.endpoints import router
from src.utils.project_version import get_project_version

app = FastAPI(
    title="MSLU ICal",
    description="MSLU ICal API documentation",
    version=get_project_version()
)
app.include_router(router, prefix="/api")
