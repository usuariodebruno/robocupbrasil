from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or "django-insecure-mude-isso-em-producao!"
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "app",
    "ckeditor",
    "django_daisy",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
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
]

ROOT_URLCONF = "rcb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.carregar_configuracao",
            ],
        },
    },
]

SILENCED_SYSTEM_CHECKS = ["ckeditor.W001", "urls.W005"]

WSGI_APPLICATION = "rcb.wsgi.application"

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
    },
}

DAISY_SETTINGS = {
    "SITE_LOGO": "/static/images/header/rcb.png",
    "SITE_TITLE": "Site RoboCup Brasil",
    "SITE_HEADER": "Site RoboCup Brasil",
    "DEFAULT_THEME": "light",
    "THEME_LIST": [
        {"name": "Claro", "value": "light"},
        {"name": "Escuro", "value": "dark"},
        {"name": "Colorido", "value": "cmyk"},
        {"name": "Drácula", "value": "dracula"},
        {"name": "Limonada", "value": "lemonade"},
        {"name": "Halloween", "value": "halloween"},
        {"name": "Jardim", "value": "garden"},
    ],
    "APPS_REORDER": {
        "admin": {
            "icon": "fa-solid fa-file-waveform",
            "name": "Gerenciar Logs",
            "hide": False,
        },
        "auth": {
            "icon": "fa-solid fa-user-lock",
            "name": "Usuários & Permissões",
            "hide": False,
        },
        "app": {
            "icon": "fa-solid fa-globe",
            "name": "Site RoboCup Brasil",
            "hide": False,
        },
    },
}