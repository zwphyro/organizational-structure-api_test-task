from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.api import router
from src.department.exceptions import DepartmentCycleError, DuplicateDepartmentNameError
import src.models  # type: ignore[no-unused-import] # NOQA: F401
from src.exceptions import NotFoundError

app = FastAPI(
    title="Organizational Structure API",
    root_path="/api/v1",
)


@app.exception_handler(NotFoundError)
def not_found_exception_handler(_, exception: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exception)},
    )


@app.exception_handler(DuplicateDepartmentNameError)
def duplicate_department_name_exception_handler(
    _, exception: DuplicateDepartmentNameError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exception)},
    )


@app.exception_handler(DepartmentCycleError)
def department_cycle_exception_handler(_, exception: DepartmentCycleError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exception)},
    )


app.include_router(router)
