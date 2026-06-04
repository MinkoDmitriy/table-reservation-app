import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api_routers import api_router
from src.core.middleware import AuthMiddleware
from src.core.exceptions import RowNotFoundError

app = FastAPI()
app.add_middleware(AuthMiddleware)

app.include_router(api_router)


@app.exception_handler(RowNotFoundError)
async def row_not_found_exception_handler(request: Request, exc: RowNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )
