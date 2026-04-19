# Документация PM Meetup

Индекс файлов в каталоге `docs/`. Подробности по приложениям — в `docs/app/*`.

## Обзор и архитектура

| Документ | Содержание |
|----------|------------|
| [codebase-overview.md](codebase-overview.md) | Карта кодовой базы: приложения Django, конфиг, фронт |
| [specification.md](specification.md) | Целевое ТЗ админ-панели (черновик требований) |
| [../README.md](../README.md) | Быстрый старт и общая информация в корне репозитория |

## API и интеграция

| Документ | Содержание |
|----------|------------|
| [api-endpoints.md](api-endpoints.md) | Сводка REST v1, префиксы, пагинация, поиск |
| [search-swagger-guide.md](search-swagger-guide.md) | Поиск `pg_trgm`, `min_rank`, работа со Swagger |

## Модели и данные

| Документ | Содержание |
|----------|------------|
| [models-draft.md](models-draft.md) | Черновик моделей и связей (сверять с кодом в `apps/`) |

Тип события vs теги vs программа (сегменты) кратко изложено в [app/events-app-documentation.md](app/events-app-documentation.md) (раздел для заказчика в конце).

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
| [../fixtures/README.md](../fixtures/README.md) | Фикстуры и `dump_fixtures` |
| [../scripts/README.md](../scripts/README.md) | Скрипты |
| [../frontend/README.md](../frontend/README.md) | Фронтенд (CRA) |

## Прочее

| Документ | Содержание |
|----------|------------|
| [admin-questions.md](admin-questions.md) | Вопросы по админке |
| [check-list-front.md](check-list-front.md) | Чек-лист для фронта |

---

**Актуальность:** при изменении URL или моделей обновляйте `api-endpoints.md`, соответствующий `app/*-documentation.md` и при необходимости [codebase-overview.md](codebase-overview.md).
