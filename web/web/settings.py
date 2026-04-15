import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV = os.environ


def env_bool(name, default=False):
    value = ENV.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = ENV.get("DJANGO_SECRET_KEY", "django-insecure-artesano-market-dev-key")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [host.strip() for host in ENV.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "WebApp",
    "servicios",
    "blog",
    "contacto",
    "carro",
    "pagos",
    "cuentas",
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

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "carro.context_processor.importe_total_carro",
            ],
        },
    },
]

WSGI_APPLICATION = "web.wsgi.application"

if ENV.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": ENV.get("POSTGRES_DB", "artesano_db"),
            "USER": ENV.get("POSTGRES_USER", "postgres"),
            "PASSWORD": ENV.get("POSTGRES_PASSWORD", ""),
            "HOST": ENV.get("POSTGRES_HOST", "127.0.0.1"),
            "PORT": ENV.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "WebApp" / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = ENV.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = ENV.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_PORT = int(ENV.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = ENV.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = ENV.get("EMAIL_HOST_PASSWORD", "")

PAYPAL_CLIENT_ID = ENV.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = ENV.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_BASE_URL = ENV.get("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")

LOGIN_URL = "/cuentas/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
