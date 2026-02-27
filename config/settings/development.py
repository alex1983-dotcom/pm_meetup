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

