"""Configurações do microsserviço pedagógico."""
import os
import urllib.parse
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

_DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "5"))
_POOL_OPTIONS: dict[str, Any] = {
    "POOL_SIZE": _DB_POOL_SIZE,
    "MAX_OVERFLOW": 0,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
    "PRE_PING": True,
}


def _parse_db_url(url: Any) -> dict[str, Any]:
    """Faz o parse de uma URL PostgreSQL para dict de configuração Django.
    Se a URL estiver vazia, retorna SQLite em memória (útil para testes/local).
    """
    if not url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }

    if isinstance(url, bytes):
        url = url.decode("utf-8")

    parsed = urllib.parse.urlparse(str(url))
    return {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "postgres",
        "PASSWORD": parsed.password or "postgres",
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
        "POOL_OPTIONS": _POOL_OPTIONS,
        "TEST": {"MIGRATE": False}, 
    }


SILENCED_SYSTEM_CHECKS = [
    "models.W035",  # db_table duplicado entre apps (intencional por multi-db)
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.componentes_curriculares",
    "apps.turmas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "pedagogico": _parse_db_url(os.environ.get("URL_BANCO_PEDAGOGICO", "")),
}

API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "x-api-key")
API_KEY = os.environ.get("API_KEY", "dev-key-default")

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-MS-Pedagogico API",
    "DESCRIPTION": "Microsserviço pedagógico EOL",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKey": {
                "type": "apiKey",
                "name": API_KEY_HEADER,
                "in": "header",
            }
        }
    },
    "SECURITY": [{"ApiKey": []}],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_TZ = True
USE_I18N = True
