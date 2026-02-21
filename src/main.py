from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.api import router
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


app.include_router(router)
