from fastapi import FastAPI
from src.api import router

from src.department.models import Department  # type: ignore[no-unused-import] # NOQA: F401
from src.employee.models import Employee  # type: ignore[no-unused-import] # NOQA: F401

app = FastAPI(
    title="Redirect URLs Management API",
    root_path="/api/v1",
)

app.include_router(router)
