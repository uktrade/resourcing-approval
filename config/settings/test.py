from .base import *  # noqa: F403


DATABASES["default"] = dj_database_url.parse(
    "postgres://postgres:postgres@postgres:5432/resourcing-approval"
)

CELERY_BROKER_URL = "redis://redis:6379/0"
