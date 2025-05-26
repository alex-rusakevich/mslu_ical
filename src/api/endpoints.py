from fastapi import APIRouter

from src.api.students import router as students_router
from src.api.teachers import router as teachers_router

router = APIRouter()
router.include_router(teachers_router, prefix="/teachers")
router.include_router(students_router, prefix="/students")
