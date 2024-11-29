import datetime
import os
from pathlib import Path

from dotenv import load_dotenv

from core.infrastructure.log_services.services import CustomisedJSONFormatter

# Load envirnment Varibales
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG")))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

# Application definition

INSTALLED_APPS = [
    # Internal Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # External Apps
    "core.domain.users",
    # Third-Party Apps
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.interface.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "core.driver.asgi.application"
WSGI_APPLICATION = "core.driver.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}

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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static File Configurations
STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "core/static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User Authentication Functionality
AUTH_USER_MODEL = "users.User"
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:home"
LOGOUT_REDIRECT_URL = "users:login"

# CELERY
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Sendgrid Configurations
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM_MAIL = os.environ.get("SENDGRID_FROM_MAIL")

# Sendgrid Templates
SENDGRID_VERIFY_EMAIL_TEMPLATE_KEY = os.environ.get(
    "SENDGRID_VERIFY_EMAIL_TEMPLATE_KEY"
)
SENDGRID_FORGOT_PASSWORD_TEMPLATE_KEY = os.environ.get(
    "SENDGRID_FORGOT_PASSWORD_TEMPLATE_KEY"
)
SENDGRID_FORGOT_PASSWORD_COMPLETED_TEMPLATE_KEY = os.environ.get(
    "SENDGRID_FORGOT_PASSWORD_COMPLETED_TEMPLATE_KEY"
)

# Logger Setting
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": CustomisedJSONFormatter,
        },
    },
    "handlers": {
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": f"logs/debug/{datetime.datetime.utcnow().date()}_debug.log",
            "formatter": "json",
        },
        "info_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": f"logs/info/{datetime.datetime.utcnow().date()}_info.log",
            "formatter": "json",
        },
        "warn_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": f"logs/warning/{datetime.datetime.utcnow().date()}_warn.log",
            "formatter": "json",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": f"logs/error/{datetime.datetime.utcnow().date()}_error.log",
            "formatter": "json",
        },
        "custom_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": f"logs/custom/{datetime.datetime.utcnow().date()}_custom.log",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["debug_file", "info_file", "warn_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "custom_logger": {
            "handlers": [
                "custom_file",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}
