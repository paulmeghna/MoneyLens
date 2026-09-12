import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]

    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    )

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.strip()

        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )

        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or (
        "sqlite:///"
        + os.path.join(BASE_DIR, "instance", "database.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False