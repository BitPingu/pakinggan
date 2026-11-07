import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.routers.albums import router as albums_router
from app.routers.artists import router as artists_router
from app.routers.tracks import router as tracks_router
from app.routers.users import router as users_router

logger = logging.getLogger(__name__)

# init fastapi app
app = FastAPI()


# handler for sqlalchemy database exceptions
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # record request path and exception traceback
    logger.error(
        "Database error while processing %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    # return generic http 500 response
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


# middleware that processes requests and responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(users_router)
app.include_router(artists_router)
app.include_router(albums_router)
app.include_router(tracks_router)


# root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Pakinggan API"}


# checks whether fastapi is running
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# checks postgresql connectivity
@app.get("/api/db-health")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}
