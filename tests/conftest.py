import pytest
from app import app
from models import db


@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + str(database_path)
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client