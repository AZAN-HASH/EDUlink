import os
from datetime import timedelta

from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

load_dotenv()

database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/edulink")


def _parse_origins(value):
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    IS_PRODUCTION = APP_ENV == "production"
    DEBUG = not IS_PRODUCTION

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-please-change-this-32chars")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-please-change-this")
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        if database_url in {"sqlite://", "sqlite:///:memory:"}
        else {}
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")

    CORS_ORIGINS = _parse_origins(os.getenv("CORS_ORIGINS")) or [CLIENT_URL]
    SOCKET_CORS_ORIGINS = (
        _parse_origins(os.getenv("SOCKET_CORS_ORIGINS"))
        or (["*"] if not IS_PRODUCTION else CORS_ORIGINS)
    )
