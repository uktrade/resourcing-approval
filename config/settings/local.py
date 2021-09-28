from .base import *


DEBUG = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DATABASES["default"] = dj_database_url.parse(
    "postgres://postgres:postgres@postgres:5432/contractor-approval"
)
