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