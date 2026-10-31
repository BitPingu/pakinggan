from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine
from app.routers.artists import router as artists_router


# init fastapi app
app = FastAPI()


# middleware that processes requests and responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# register artists router
app.include_router(artists_router)


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

