"""Application configuration loaded from environment variables."""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _normalize_db_url(url: str) -> str:
    # SQLAlchemy 2.x + psycopg3 expects the "postgresql+psycopg" dialect.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_EXPIRES_SECONDS", "3600")))

    _raw_db = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = (
        _normalize_db_url(_raw_db)
        if _raw_db
        else "sqlite:///" + os.path.join(BASE_DIR, "juniorswipe_dev.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5501,http://127.0.0.1:5501",
        ).split(",")
        if o.strip()
    ]

    STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(BASE_DIR, "storage"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
    SEED_ON_STARTUP = os.environ.get("SEED_ON_STARTUP", "true").lower() == "true"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET = "test-secret"
    JWT_EXPIRES = timedelta(seconds=3600)
    SEED_ON_STARTUP = False
    STORAGE_DIR = os.path.join(BASE_DIR, "storage_test")


def get_config(name: str | None = None):
    if (name or os.environ.get("FLASK_CONFIG", "")).lower() in ("test", "testing"):
        return TestConfig
    return Config
