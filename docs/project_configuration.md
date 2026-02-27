# Конфигурация проекта

## config/settings/base.py
```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'django_ckeditor_5',
    
    # Local apps
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === БАЗА ДАННЫХ ===
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='pm_meetup'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Minsk'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# === СТАТИКА  ===
STATICFILES_DIRS = [BASE_DIR / 'static']

# Добавляем build-папку фронтенда, только если она существует
# Это убирает предупреждение staticfiles.W004 в режиме разработки
frontend_build_static = BASE_DIR / 'frontend' / 'build' / 'static'
if frontend_build_static.exists():
    STATICFILES_DIRS.append(frontend_build_static)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'PM Meetup API',
    'VERSION': '1.0.0',
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
```

## config/settings/development.py

```python
from .base import *
import pathlib

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Логирование
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
for log_name in ("django.log", "drf.log"):
    pathlib.Path(LOG_DIR / log_name).write_text("", encoding="utf-8")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "django.log",
            "mode": "a",
            "encoding": "utf-8",
            "formatter": "verbose",
          },
        "drf_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "drf.log",
            "mode": "a",
            "encoding": "utf-8",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["file"], "level": "ERROR", "propagate": False},
        "rest_framework": {"handlers": ["drf_file"], "level": "WARNING", "propagate": False},
    },
}
# Отключаем шумные логи сервера в dev
LOGGING['loggers']['django.server'] = {
    'handlers': ['console'],
    'level': 'WARNING',
    'propagate': False,
}
```

---

## config/settings/production.py
```python
from .base import *
from decouple import config
from pathlib import Path


DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# === БАЗА ДАННЫХ ===
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='pm_meetup'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}



LOG_DIR = Path(config("LOG_DIR", default="/var/log/pm_meetup"))
LOG_DIR.mkdir(mode=0o755, exist_ok=True)

# общий формат
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "WARNING",
        },
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 МБ
            "backupCount": 5,
            "formatter": "verbose",
            "level": "WARNING",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console", "file_info", "file_error"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file_info"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        "rest_framework": {
            "handlers": ["file_info"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# опциональный INFO-хендлер (1 день, 10 МБ)
if config("ENABLE_INFO_LOG", default=False, cast=bool):
    LOGGING["handlers"]["info_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_DIR / "info.log",
        "maxBytes": 10 * 1024 * 1024,
        "backupCount": 1,  # храним 1 сутки
        "formatter": "verbose",
        "level": "INFO",
    }
    # цепляем к корневому логгеру
    LOGGING["root"]["handlers"].append("info_file")

# после создания файла сразу закрываем права 640
if ENABLE_INFO_LOG := config("ENABLE_INFO_LOG", default=False, cast=bool):

    def _set_info_perms():
        try:
            (LOG_DIR / "info.log").chmod(0o640)
        except FileNotFoundError:
            pass

    # вызовем после конфигурации
    import atexit
    atexit.register(_set_info_perms)

# # --------------- почта админам при ERROR -------------------------------------
# ADMINS = [(config("ADMIN_NAME", default="Admin"), config("ADMIN_EMAIL"))]
# SERVER_EMAIL = config("SERVER_EMAIL", default="errors@hub42.ru")
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = config("EMAIL_HOST", default="smtp.yandex.ru")
# EMAIL_PORT = config("EMAIL_PORT", default=465, cast=int)
# EMAIL_USE_SSL = True
# EMAIL_HOST_USER = config("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# --------------- статика / медиа ---------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"


# --------------- безопасность -------------------------------------------------
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```
## .env

```ini
# Django
DEBUG=1
SECRET_KEY=django-insecure-dev-key-change-in-prod

# База данных для локальной работы
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pm_meetup
DB_USER=postgres
DB_PASSWORD=пароль
DB_HOST=db
DB_PORT=5432

# Для контейнера PostgreSQL
POSTGRES_DB=pm_meetup
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль

# Email (опционально)
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

