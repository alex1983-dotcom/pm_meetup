# Документация PM Meetup

Единая точка входа: отсюда переходите к разделам. Подробные черновики и Obsidian-заметки лежат в `obsidian_pm_meetup/`.

## Обзор и архитектура

| Документ | Содержание |
|----------|------------|
| [codebase-overview.md](codebase-overview.md) | Карта всей кодовой базы: приложения Django, конфиг, фронт, скрипты |
| [obsidian_pm_meetup/specification.md](obsidian_pm_meetup/specification.md) | Спецификация / требования (если ведётся) |
| [obsidian_pm_meetup/project_configuration.md](obsidian_pm_meetup/project_configuration.md) | Переменные окружения и конфигурация |

## API и интеграция

| Документ | Содержание |
|----------|------------|
| [obsidian_pm_meetup/api-endpoints.md](obsidian_pm_meetup/api-endpoints.md) | Сводка REST v1, префиксы, пагинация, поиск |
| [obsidian_pm_meetup/search-swagger-guide.md](obsidian_pm_meetup/search-swagger-guide.md) | Поиск `pg_trgm`, `min_rank`, работа со Swagger |
| [obsidian_pm_meetup/api_powershell/README.md](obsidian_pm_meetup/api_powershell/README.md) | Примеры запросов из PowerShell |

## Модели и данные

| Документ | Содержание |
|----------|------------|
| [event-type-vs-categories.md](event-type-vs-categories.md) | **Для заказчика:** тип события, теги и программа (сегменты) — без отдельной «тематики» |
| [obsidian_pm_meetup/models-codebase.md](obsidian_pm_meetup/models-codebase.md) | Код моделей в одном месте (справочник) |
| [obsidian_pm_meetup/models-relations-diagram.md](obsidian_pm_meetup/models-relations-diagram.md) | Связи между сущностями |
| [obsidian_pm_meetup/model-schema-graph.md](obsidian_pm_meetup/model-schema-graph.md) | Схема графа моделей |
| [obsidian_pm_meetup/models-draft.md](obsidian_pm_meetup/models-draft.md) | Черновики / заметки по моделям |

## Документация по приложениям Django (`apps/*`)

| Приложение | Файл |
|------------|------|
| core | [app/core-app-documentation.md](obsidian_pm_meetup/app/core-app-documentation.md) |
| users | [app/users-app-documentation.md](obsidian_pm_meetup/app/users-app-documentation.md) |
| events | [app/events-app-documentation.md](obsidian_pm_meetup/app/events-app-documentation.md) |
| news | [app/news-app-documentation.md](obsidian_pm_meetup/app/news-app-documentation.md) |
| content | [app/content-app-documentation.md](obsidian_pm_meetup/app/content-app-documentation.md) |
| pages | [app/pages-app-documentation.md](obsidian_pm_meetup/app/pages-app-documentation.md) |
| materials | [app/materials-app-documentation.md](obsidian_pm_meetup/app/materials-app-documentation.md) |

PDF-копии части документов: `obsidian_pm_meetup/app_pdf/`.

## Инфраструктура и процессы

| Документ | Содержание |
|----------|------------|
| [obsidian_pm_meetup/docker-commands.md](obsidian_pm_meetup/docker-commands.md) | Docker Compose, сборка, типовые команды |
| [../fixtures/README.md](../fixtures/README.md) | Фикстуры |
| [../scripts/README.md](../scripts/README.md) | Скрипты |
| [../frontend/README.md](../frontend/README.md) | Фронтенд (CRA) |

## Прочее

| Документ | Содержание |
|----------|------------|
| [obsidian_pm_meetup/admin-questions.md](obsidian_pm_meetup/admin-questions.md) | Вопросы по админке |
| [obsidian_pm_meetup/check-list-front.md](obsidian_pm_meetup/check-list-front.md) | Чек-лист для фронта |

---

**Актуальность:** при изменении URL или моделей обновляйте `api-endpoints.md`, соответствующий `app/*-documentation.md` и при необходимости [codebase-overview.md](codebase-overview.md).
