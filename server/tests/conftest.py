import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.core.config import settings
from app.database import Base, get_db
from app.main import app


# Creates a database engine for the test session.
@pytest.fixture(scope="session")
def test_engine():
    # Verifies that the test database URL is configured.
    if not settings.TEST_DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL is not configured in .env")

    # Extracts and validates the test database name.
    database_name = make_url(settings.TEST_DATABASE_URL).database

    if database_name != "pakinggan_test":
        pytest.fail(
            "Refusing to run tests: TEST_DATABASE_URL must point to pakinggan_test"
        )

    # Creates an engine connected to the test database.
    engine = create_engine(settings.TEST_DATABASE_URL)

    # Recreates the database schema before running tests.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    # Removes the test tables and releases the engine resources.
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# Creates an isolated database session for each test.
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    # Creates a session that uses a savepoint within the test transaction.
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        # Closes the session and rolls back the test transaction.
        session.close()
        transaction.rollback()
        connection.close()


# Creates a FastAPI test client with an overridden database dependency.
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    # Overrides the database dependency for the duration of the test.
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Removes the dependency override after the test.
        app.dependency_overrides.clear()


# Creates a test user.
@pytest.fixture
def user(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "gavin",
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )
    return response.json()


# Creates a test artist.
@pytest.fixture
def artist(client):
    response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )
    return response.json()


# Creates a test album associated with the test artist.
@pytest.fixture
def album(client, artist):
    response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist["id"],
        },
    )
    return response.json()


# Creates a test track associated with the test album.
@pytest.fixture
def track(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    return response.json()
