from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'django_extensions',
    'mdeditor',
    'docutils',
    
    # Local apps
    'apps.core',
    'apps.users',
    'apps.events',
    'apps.news',
    'apps.content',
    'apps.pages',
    'apps.materials',
]

AUTH_USER_MODEL = 'users.User'

# django.contrib.sites: иначе get_current_site() ищет Site по Host (localhost) и не находит
# запись по умолчанию (example.com) → Site.DoesNotExist на /admin/login/ и др.
SITE_ID = 1

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

# Фикстуры для фронта и тестов (loaddata ищет здесь и в app/fixtures/)
FIXTURE_DIRS = [BASE_DIR / 'fixtures']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# 13. Django REST Framework
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ["apps.core.permissions.DocsOrApiKey"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}


# --------------------------------------------------
# 15. DRF-Spectacular (Swagger/OpenAPI)
# --------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "PM Meetup API",
    "DESCRIPTION": "Документация REST API проекта PM Meetup. Все эндпоинты для фронтенда: события, новости, контент, материалы.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "core", "description": "Теги (для фильтров событий и новостей)"},
        {"name": "events", "description": "События, категории, спикеры, сегменты программы, галереи, регистрации"},
        {"name": "news", "description": "Новости и статьи"},
        {"name": "content", "description": "Партнёры, команда, настройки сайта, статичные страницы, заявки на партнёрство"},
        {"name": "materials", "description": "Материалы и категории материалов"},
        {"name": "pages", "description": "Страницы с блоками (конструктор для фронта)"},
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-KEY",
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')

# MDEditor (Markdown)
X_FRAME_OPTIONS = 'SAMEORIGIN'  # требуется для mdeditor в Django 3.0+
MDEDITOR_CONFIGS = {
    'default': {
        'width': '90%',
        'height': 500,
        'toolbar': [
            "undo", "redo", "|",
            "bold", "del", "italic", "quote", "|",
            "h1", "h2", "h3", "h5", "h6", "|",
            "list-ul", "list-ol", "hr", "|",
            "link", "image", "code", "table", "|",
            "preview", "fullscreen",
        ],
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
        'upload_require_auth': False,
        'image_folder': 'editor',
        'theme': 'default',
        'preview_theme': 'default',
        'editor_theme': 'default',
        'language': 'en',
    },
}
