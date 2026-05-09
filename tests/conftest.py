import pytest
import tempfile
import os
from app import create_app
from app.db import get_db, init_db


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    test_app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })

    yield test_app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Get database connection for direct queries in tests."""
    with app.app_context():
        yield get_db()