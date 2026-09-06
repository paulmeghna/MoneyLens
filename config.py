import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR, "instance", "database.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False