import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from src.api_routers import api_router
from src.core.middleware import AuthMiddleware
from src.core.exceptions import RowNotFoundError

import os
from fastapi.staticfiles import StaticFiles

from src.core.config import settings
from src.core.storage import get_storage, S3Storage

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    if settings.STORAGE_TYPE.lower() == "s3":
        storage = get_storage()
        if isinstance(storage, S3Storage):
            try:
                await storage.init_bucket()
            except Exception as e:
                print(f"CRITICAL: Failed to auto-initialize S3 bucket: {e}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# Ensure static directories exist and mount static files serving
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)


@app.exception_handler(RowNotFoundError)
async def row_not_found_exception_handler(request: Request, exc: RowNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )
