# Документация PM Meetup

Корень Obsidian-vault и индекс файлов в **`docs_pm_meetup/`**. Подробности по приложениям — в `app/*`.

**`specification.md`** — целевое ТЗ (может опережать код). **`Daily-Notes/office-and-dev-slang.md`** — словарь терминов, не описание продукта.

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
| [api_powershell/README.md](api_powershell/README.md) | Запросы к API из PowerShell |

## Модели и данные

| Документ | Содержание |
|----------|------------|
| [models-draft.md](models-draft.md) | Набросок моделей и связей (сверять с `apps/*/models.py`) |
| [models-codebase.md](models-codebase.md) | Выжимка `apps/*/models.py` для Obsidian |
| [models-relations-diagram.md](models-relations-diagram.md) | Mermaid-схемы связей |
| [model-schema-graph.md](model-schema-graph.md) | Генерация DOT-графа моделей |

Тип события vs теги vs программа (сегменты) — в [app/events-app-documentation.md](app/events-app-documentation.md).

## Документация по приложениям Django (`apps/*`)

| Приложение | Файл | PDF |
|------------|------|-----|
| core | [app/core-app-documentation.md](app/core-app-documentation.md) | [app_pdf/core-app-documentation.pdf](app_pdf/core-app-documentation.pdf) |
| users | [app/users-app-documentation.md](app/users-app-documentation.md) | [app_pdf/users-app-documentation.pdf](app_pdf/users-app-documentation.pdf) |
| events | [app/events-app-documentation.md](app/events-app-documentation.md) | [app_pdf/events-app-documentation.pdf](app_pdf/events-app-documentation.pdf) |
| news | [app/news-app-documentation.md](app/news-app-documentation.md) | [app_pdf/news-app-documentation.pdf](app_pdf/news-app-documentation.pdf) |
| content | [app/content-app-documentation.md](app/content-app-documentation.md) | [app_pdf/content-app-documentation.pdf](app_pdf/content-app-documentation.pdf) |
| pages | [app/pages-app-documentation.md](app/pages-app-documentation.md) | — |
| materials | [app/materials-app-documentation.md](app/materials-app-documentation.md) | [app_pdf/materials-app-documentation.pdf](app_pdf/materials-app-documentation.pdf) |

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
| [Daily-Notes/office-and-dev-slang.md](Daily-Notes/office-and-dev-slang.md) | Словарь офисных и dev-терминов |
| [hols_PM_MEETUP.canvas](hols_PM_MEETUP.canvas) | Obsidian Canvas — обзорная схема |
| `media/` | Скриншоты макетов |

---

**Актуальность:** при изменении URL, моделей или прав доступа обновляйте `api-endpoints.md`, `auth-sessions.md`, соответствующий `app/*-documentation.md` и при необходимости [codebase-overview.md](codebase-overview.md).
