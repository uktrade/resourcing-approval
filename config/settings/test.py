from .non_prod import *  # noqa: F403


APP_ENV = "test"

ALLOWED_HOSTS = ["testrunner"]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DATABASES["default"] = dj_database_url.parse(
    "postgres://postgres:postgres@postgres:5432/resourcing-approval"
)

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_TASK_ALWAYS_EAGER = True

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_ROOT = BASE_DIR / "media"
