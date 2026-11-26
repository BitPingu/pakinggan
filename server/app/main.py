import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database import engine
from app.routers.albums import router as albums_router
from app.routers.artists import router as artists_router
from app.routers.lastfm import router as lastfm_router
from app.routers.listening_history import router as listening_history_router
from app.routers.tracks import router as tracks_router
from app.routers.users import router as users_router

# Configures application logging.
logger = logging.getLogger(__name__)

# Initializes the FastAPI application.
app = FastAPI()


# Handles SQLAlchemy database exceptions.
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Logs the request path and exception traceback.
    logger.error(
        "Database error while processing %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    # Returns a generic HTTP 500 response.
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


# Configures cross-origin requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registers the application API routers.
app.include_router(users_router)
app.include_router(artists_router)
app.include_router(albums_router)
app.include_router(tracks_router)
app.include_router(lastfm_router)
app.include_router(listening_history_router)


# Returns a welcome message from the API.
@app.get("/")
def root():
    return {"message": "Welcome to Pakingan API"}


# Checks whether the FastAPI application is running.
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Checks connectivity to the PostgreSQL database.
@app.get("/api/db-health")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}
