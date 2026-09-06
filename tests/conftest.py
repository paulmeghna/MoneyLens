import pytest
from app import app
from models import db
@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(database_path)
    )
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client
@pytest.fixture
def csrf_client(client):
    app.config["WTF_CSRF_ENABLED"] = True
    yield client
    # Restore the normal functional-test configuration.
    app.config["WTF_CSRF_ENABLED"] = False
