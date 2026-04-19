# PM Meetup

Бэкенд на **Django 6** + **Django REST Framework**, фронтенд — **React** (Create React App). REST API версии `v1`, документация OpenAPI в **Swagger UI** (`/api/docs/`).

## Быстрый старт

1. Скопируйте переменные окружения из [`.env.example`](.env.example) в `.env` (`SECRET_KEY`, `DEBUG`, параметры БД; для фронта на другом порту — `CORS_ALLOWED_ORIGINS`). Значения `POSTGRES_*` и `DB_*` для пароля должны совпадать.
2. **Docker:** `docker compose up --build` — поднимутся PostgreSQL, Django на `:8000`, фронт на `:3000`.
3. **Локально (без Docker):** виртуальное окружение, `pip install -r requirements.txt`, PostgreSQL с расширением `pg_trgm`, `python manage.py migrate`, `python manage.py runserver`.

Подробные команды и прод-сборка: [`docs/docker-commands.md`](docs/docker-commands.md).

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `config/` | URL, `settings` (base / development / production), WSGI/ASGI |
| `apps/core/` | Теги, API-ключи, общие модели и сериализаторы, middleware поиска |
| `apps/users/` | Кастомная модель пользователя (вход по email) |
| `apps/events/` | События, спикеры, сегменты программы, галереи, регистрации |
| `apps/news/` | Новости |
| `apps/content/` | Партнёры, команда, настройки сайта, статичные страницы, заявки на партнёрство |
| `apps/pages/` | Страницы-конструкторы (блоки) для фронта |
| `apps/materials/` | Материалы и категории |
| `frontend/` | React-приложение |
| `fixtures/` | JSON-фикстуры для тестов и демо-данных |
| `scripts/` | Вспомогательные скрипты |
| `docs/` | Индекс документации (`docs/README.md`), Docker, API, приложения (`docs/app/*`) |

Полная карта модулей и файлов: [`docs/codebase-overview.md`](docs/codebase-overview.md). Оглавление всех документов: [`docs/README.md`](docs/README.md).

## API

- **Swagger:** `http://localhost:8000/api/docs/`
- **Сводка эндпоинтов:** [`docs/api-endpoints.md`](docs/api-endpoints.md)
- Доступ к API: заголовок `X-API-KEY` (ключ из админки) или запрос с доверенного origin (например `http://localhost:3000`). Исключение: схема и Swagger UI открыты без ключа.

## Разработка

- Миграции: `python manage.py makemigrations` / `migrate`
- Фикстуры: см. [`fixtures/README.md`](fixtures/README.md)
- Команды: `dump_fixtures`, `seed_data` в `apps/core/management/commands/`

## Лицензия и контакты

Уточните в репозитории при публикации (файл лицензии при необходимости добавьте отдельно).
