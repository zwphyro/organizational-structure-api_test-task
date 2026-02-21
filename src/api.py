from fastapi import APIRouter
from src.department.routes import router as department_router

router = APIRouter()

router.include_router(department_router, prefix="/departments")
