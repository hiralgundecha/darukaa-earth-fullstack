import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://darukaa:darukaa@localhost:5432/darukaa"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
