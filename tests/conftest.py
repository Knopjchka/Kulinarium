import os

import pytest

# Ensure tests use an isolated test database file
os.environ["DATABASE_URL"] = "sqlite://test_db.sqlite3"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Sets up an isolated test database and cleans up afterward."""
    if os.path.exists("test_db.sqlite3"):
        try:
            os.remove("test_db.sqlite3")
        except OSError:
            pass

    yield

    if os.path.exists("test_db.sqlite3"):
        try:
            os.remove("test_db.sqlite3")
        except OSError:
            pass


@pytest.fixture
def client():
    """Provides a TestClient context with lifespan (Tortoise-ORM) initialized."""
    with TestClient(app) as test_client:
        yield test_client
