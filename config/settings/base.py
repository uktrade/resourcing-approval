"""
Django settings for resourcing_approval project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import dj_database_url
import environ
import sentry_sdk
from django.urls import reverse_lazy
from sentry_sdk.integrations.django import DjangoIntegration


# Setup
# See https://django-environ.readthedocs.io/en/latest/
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR / ".env")

APP_ENV = env("APP_ENV")


# Sentry
# https://docs.sentry.io/platforms/python/guides/django/
def init_sentry():
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=APP_ENV,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )


# VCAP services
# See https://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#VCAP-SERVICES

VCAP_SERVICES = env.json("VCAP_SERVICES", {})

REDIS_CREDENTIALS = VCAP_SERVICES["redis"][0]["credentials"] if VCAP_SERVICES else None


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True


# Sessions
# https://docs.djangoproject.com/en/3.2/ref/settings/#sessions

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 4 * 60 * 60  # 4 hours in seconds


# Application definition

INSTALLED_APPS = [
    "change_log.apps.ChangeLogConfig",
    "quill.apps.QuillConfig",
    "countries.apps.CountriesConfig",
    "event_log.apps.EventLogConfig",
    "chartofaccount.apps.ChartofaccountConfig",
    "user.apps.UserConfig",
    "main.apps.MainConfig",
    "dev_tools.apps.DevToolsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_celery_beat",
    "sass_processor",
    "authbroker_client",
    "django_chunk_upload_handlers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "authbroker_client.middleware.ProtectAllViewsMiddleware",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, "node_modules"),
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dev_tools.views.dev_tools_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {}
DATABASES["default"] = dj_database_url.config()


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# http://whitenoise.evans.io/en/stable/django.html

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

# Media files
# https://docs.djangoproject.com/en/3.2/ref/settings/#media-root

MEDIA_ROOT = ""
MEDIA_URL = "/media/"

# django-sass-processor
# https://github.com/jrief/django-sass-processor#using-manifeststaticfilesstorage
SASS_PROCESSOR_STORAGE = "django.contrib.staticfiles.storage.FileSystemStorage"
SASS_PROCESSOR_STORAGE_OPTIONS = {
    "location": STATIC_ROOT,
    "base_url": STATIC_URL,
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User app
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-user-model

AUTH_USER_MODEL = "user.User"

# Celery
if REDIS_CREDENTIALS:
    CELERY_BROKER_URL = (
        "rediss://:{password}@{host}:{port}/0?ssl_cert_reqs=required".format(
            **REDIS_CREDENTIALS
        )
    )


# GOV.UK Notify
GOVUK_NOTIFY_API_KEY = env("GOVUK_NOTIFY_API_KEY")
GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID = env(
    "GOVUK_NOTIFY_READY_FOR_APPROVAL_TEMPLATE_ID"
)
GOVUK_NOTIFY_APPROVED_TEMPLATE_ID = env("GOVUK_NOTIFY_APPROVED_TEMPLATE_ID")
GOVUK_NOTIFY_AMENDED_TEMPLATE_ID = env("GOVUK_NOTIFY_AMENDED_TEMPLATE_ID")
GOVUK_NOTIFY_RE_APPROVAL_TEMPLATE_ID = env("GOVUK_NOTIFY_RE_APPROVAL_TEMPLATE_ID")
GOVUK_NOTIFY_FINISHED_AMENDMENTS_REVIEW_TEMPLATE_ID = env(
    "GOVUK_NOTIFY_FINISHED_AMENDMENTS_REVIEW_TEMPLATE_ID"
)
GOVUK_NOTIFY_COMMENT_LEFT_TEMPLATE_ID = env("GOVUK_NOTIFY_COMMENT_LEFT_TEMPLATE_ID")
GOVUK_NOTIFY_APPROVAL_TEMPLATE_ID = env("GOVUK_NOTIFY_APPROVAL_TEMPLATE_ID")

# Authentication
# https://github.com/uktrade/django-staff-sso-client

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "authbroker_client.backends.AuthbrokerBackend",
]

AUTHBROKER_URL = env("AUTHBROKER_URL")
AUTHBROKER_CLIENT_ID = env("AUTHBROKER_CLIENT_ID")
AUTHBROKER_CLIENT_SECRET = env("AUTHBROKER_CLIENT_SECRET")
AUTHBROKER_STAFF_SSO_SCOPE = "read"

LOGIN_URL = reverse_lazy("authbroker_client:login")
LOGIN_REDIRECT_URL = reverse_lazy("index")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ITHC

# Set anti XSS header
SECURE_BROWSER_XSS_FILTER = True
