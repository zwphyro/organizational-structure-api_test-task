from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.api import router
from src.department.exceptions import DepartmentCycleError, DuplicateDepartmentNameError
from src.exceptions import DatabaseError, NotFoundError

import src.models  # type: ignore[no-unused-import] # NOQA: F401

app = FastAPI(title="Organizational Structure API")


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


@app.exception_handler(DatabaseError)
def database_exception_handler(_, exception: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_400_INTERNAL_SERVER_ERROR,
        content={"detail": str(exception)},
    )


app.include_router(router)
