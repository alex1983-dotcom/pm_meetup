# Обзор кодовой базы PM Meetup

Документ описывает назначение каталогов и основных файлов. Детали моделей — в [`obsidian_pm_meetup/models-codebase.md`](obsidian_pm_meetup/models-codebase.md), эндпоинты — в [`obsidian_pm_meetup/api-endpoints.md`](obsidian_pm_meetup/api-endpoints.md).

---

## Корень проекта

| Файл / каталог | Назначение |
|----------------|------------|
| `manage.py` | Точка входа Django CLI |
| `requirements.txt` | Зависимости Python (Django 6, DRF, drf-spectacular, PostgreSQL, Pillow, mdeditor и др.) |
| `Dockerfile` | Образ приложения (Python 3.12, gunicorn) |
| `docker-compose.yml` | Разработка: `db`, `web`, `frontend` |
| `docker-compose.prod.yml` | Продакшен-вариант compose (см. файл) |
| `.env` | Секреты и переменные (не коммитится; шаблон см. документацию по конфигурации) |

---

## `config/`

| Файл | Назначение |
|------|------------|
| `urls.py` | Маршруты: `admin`, `mdeditor`, Swagger (`/api/schema/`, `/api/docs/`), API `api/v1/...`, корневой include для `pages` |
| `settings/base.py` | Общие настройки: `INSTALLED_APPS`, БД PostgreSQL, DRF, Spectacular, CORS, MDEditor, `FIXTURE_DIRS` |
| `settings/development.py` | Режим разработки |
| `settings/production.py` | Продакшен |
| `wsgi.py` / `asgi.py` | Точки входа WSGI/ASGI |

---

## `apps/core/`

Общие сущности и инфраструктура API.

| Файл | Назначение |
|------|------------|
| `models.py` | `TimeStampedModel`, `Tag`, `ApiKey` |
| `views.py` | ViewSets для тегов |
| `serializers.py` | Сериализаторы тегов |
| `urls.py` | `router`: `tags` |
| `permissions.py` | `DocsOrApiKey`, `OnlyWithApiKeyOrFromFrontend` — доступ по `X-API-KEY` / query `key` или с доверенного origin |
| `middleware.py` | `LogCleanupMiddleware` — очистка лог-файлов при старте (класс есть в коде; подключение в `MIDDLEWARE` — по необходимости) |
| `admin.py` | Админка для тегов и API-ключей |
| `management/commands/dump_fixtures.py` | Выгрузка фикстур |
| `management/commands/seed_data.py` | Заполнение демо-данными |
| `migrations/` | В т.ч. включение расширения `pg_trgm` |

---

## `apps/users/`

| Файл | Назначение |
|------|------------|
| `models.py` | `User` на базе `AbstractUser`, вход по **email** (`USERNAME_FIELD`), роли, аватар |
| `serializers.py` | Сериализаторы пользователя для API |
| `admin.py` | Управление пользователями |

Отдельного `urls.py` под публичный REST в корневом `config/urls` нет — пользователи подключаются через сессии DRF там, где нужна авторизация (например регистрации на события).

---

## `apps/events/`

События митапов: тематики (для внутренней аналитики), спикеры, программа (сегменты), галереи, регистрации.

| Файл | Назначение |
|------|------------|
| `models.py` | Тематики (`EventTheme`), события, спикеры, сегменты, галереи, регистрации, связи с тегами |
| `views.py` | ViewSets |
| `serializers.py` | Сериализаторы и вложенные представления |
| `urls.py` | `themes`, `speakers`, `events`, `segments`, `galleries`, `registrations` |
| `admin.py` | Админка |
| `migrations/` | Индексы для trigram-поиска по событиям |

---

## `apps/news/`

| Файл | Назначение |
|------|------------|
| `models.py` | Статьи новостей, теги, публикация |
| `views.py` / `serializers.py` / `urls.py` | `articles` — список и деталь по slug |
| `migrations/` | Trgm для поиска |

---

## `apps/content/`

Контент сайта: партнёры, команда, глобальные настройки, статичные страницы контента, заявки на партнёрство.

| Файл | Назначение |
|------|------------|
| `models.py` | Партнёры, участники команды, настройки сайта, страницы, заявки |
| `urls.py` | `partners`, `team`, `settings`, `static-pages`, `partnership-applications` |
| `views.py` | ViewSets, в т.ч. POST заявок без обязательной авторизации (по политике проекта) |

---

## `apps/pages/`

Страницы с **блочной вёрсткой** для фронтенда (конструктор).

| Файл | Назначение |
|------|------------|
| `models.py` | Страница, блоки, элементы блоков |
| `views.py` | `PageDetailAPIView` — отдаёт структуру по `slug` |
| `urls.py` | `GET .../api/pages/<slug>/` (префикс задаётся в `config` через `include`) |

---

## `apps/materials/`

Материалы (записи, презентации) и категории.

| Файл | Назначение |
|------|------------|
| `models.py` | Категории, материалы, метаданные |
| `urls.py` | `categories`, `materials` с фильтрами и поиском |
| `migrations/` | Trgm для материалов |

---

## `templates/` и статика

Шаблоны Django (если используются не только админка). Статика: `static/`, собранный фронт может подключаться через `STATICFILES_DIRS` → `frontend/build/static`.

---

## `frontend/`

Приложение на **Create React App** (`react-scripts`). Точка входа: `src/index.js`, корневой компонент `src/App.js`. Прокси на бэкенд задаётся в `package.json` (`http://web:8000` для Docker).

---

## `fixtures/`

JSON-фикстуры для `loaddata`; путь указан в `FIXTURE_DIRS`. См. [`fixtures/README.md`](../fixtures/README.md).

---

## `scripts/`

Вспомогательные скрипты (например `fetch_page.py`). См. [`scripts/README.md`](../scripts/README.md).

---

## `commits/`

Текстовые заметки к коммитам (если ведёте такой формат работы).

---

## Поток запроса API (упрощённо)

1. Запрос попадает в DRF с `DEFAULT_PERMISSION_CLASSES = DocsOrApiKey`.
2. Для путей `/api/schema/`, `/api/docs/` доступ без ограничений.
3. Иначе проверяется API-ключ или origin/referer с локальных хостов фронта и Swagger.

---

## Связанные документы

- [README.md](../README.md) — быстрый старт в корне репозитория  
- [docs/README.md](README.md) — полное оглавление документации  
