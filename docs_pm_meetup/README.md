# Документация PM Meetup

Индекс файлов в каталоге **`docs_pm_meetup/`**. Подробности по приложениям — в `app/*`.

## Обзор и архитектура

| Документ | Содержание |
|----------|------------|
| [codebase-overview.md](codebase-overview.md) | Карта кодовой базы: приложения Django, конфиг, фронт |
| [specification.md](specification.md) | Целевое ТЗ админ-панели (черновик требований) |
| [project_configuration.md](project_configuration.md) | Переменные `.env` и настройки Django |
| [../README.md](../README.md) | Быстрый старт в корне репозитория |

## API и интеграция

| Документ | Содержание |
|----------|------------|
| [api-endpoints.md](api-endpoints.md) | Сводка REST v1, префиксы, пагинация, поиск |
| [auth-sessions.md](auth-sessions.md) | API-ключ, origin, сессия, видимость контента |
| [search-swagger-guide.md](search-swagger-guide.md) | Поиск `pg_trgm`, `min_rank`, работа со Swagger |
| [static-assets-without-api.md](static-assets-without-api.md) | Постоянные картинки без API: Django `static/` vs CRA `public`/`src` |

## Модели и данные

| Документ | Содержание |
|----------|------------|
| [models-draft.md](models-draft.md) | Набросок моделей и связей (сверять с `apps/*/models.py`) |

Тип события vs теги vs программа (сегменты) — в [app/events-app-documentation.md](app/events-app-documentation.md).

## Документация по приложениям Django (`apps/*`)

| Приложение | Файл |
|------------|------|
| core | [app/core-app-documentation.md](app/core-app-documentation.md) |
| users | [app/users-app-documentation.md](app/users-app-documentation.md) |
| events | [app/events-app-documentation.md](app/events-app-documentation.md) |
| news | [app/news-app-documentation.md](app/news-app-documentation.md) |
| content | [app/content-app-documentation.md](app/content-app-documentation.md) |
| pages | [app/pages-app-documentation.md](app/pages-app-documentation.md) |
| materials | [app/materials-app-documentation.md](app/materials-app-documentation.md) |

## Инфраструктура и процессы

| Документ | Содержание |
|----------|------------|
| [docker-commands.md](docker-commands.md) | Docker Compose, типовые команды |
| [nginx-production.md](nginx-production.md) | Nginx в проде: пути конфига, TLS, Let's Encrypt |
| [../fixtures/README.md](../fixtures/README.md) | Фикстуры и `dump_fixtures` |
| [../scripts/README.md](../scripts/README.md) | Скрипты |
| [../frontend/README.md](../frontend/README.md) | Фронтенд (CRA) |

## Прочее

| Документ | Содержание |
|----------|------------|
| [admin-questions.md](admin-questions.md) | Вопросы по админке и сводка «что уже в коде» |
| [check-list-front.md](check-list-front.md) | Чек-лист для фронтенд-разработчика |

---

**Актуальность:** при изменении URL, моделей или прав доступа обновляйте `api-endpoints.md`, `auth-sessions.md`, соответствующий `app/*-documentation.md` и при необходимости [codebase-overview.md](codebase-overview.md).
