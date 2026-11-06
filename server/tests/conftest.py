import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.core.config import settings
from app.database import Base, get_db
from app.main import app


# provide a db connection in every test (shared across the test run)
# Connects to pakinggan_test and prepares tables once
@pytest.fixture(scope="session")
def test_engine():
    # check test db url
    if not settings.TEST_DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL is not configured in .env")

    # extract db name
    database_name = make_url(settings.TEST_DATABASE_URL).database

    # verify db name
    if database_name != "pakinggan_test":
        pytest.fail(
            "Refusing to run tests: TEST_DATABASE_URL must point to pakinggan_test"
        )

    # create sqlalchemy engine connected to db
    engine = create_engine(settings.TEST_DATABASE_URL)

    # Recreate the schema in the dedicated test database.
    # each new pytest run starts with an empty set of tables
    Base.metadata.drop_all(bind=engine) # remove tables
    Base.metadata.create_all(bind=engine) # create tables

    # setup then teardown
    yield engine

    # Clean up after the test session.
    Base.metadata.drop_all(bind=engine) # remove test tables
    engine.dispose() # dispose resources


# provide a db session to individual tests
# Creates a new transaction for each test
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect() # open connection to postgresql
    transaction = connection.begin() # begin db transaction

    # create sqlalchemy session
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint", # use a savepoint within existing transaction
    )

    try:
        yield session # receive the session
    finally:
        session.close() # close the sqlalchemy session
        transaction.rollback() # undo changes in outer transaction
        connection.close() # release the db connection


# provide a fastapi test client
# Overrides get_db and creates the FastAPI test client
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session # provide the test session
        except Exception:
            db_session.rollback() # revert transaction for the test
            raise

    # override get_db with override_get_db
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client # create a client that can send requests to app
    finally:
        app.dependency_overrides.clear() # remove dependency overrides

