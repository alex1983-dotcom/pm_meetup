# REST API — сводка эндпоинтов для фронтенда

Все эндпоинты доступны при передаче заголовка **`X-API-KEY`** (активный ключ из админки) или при запросе с доверенного источника (например, frontend на localhost:3000). Исключение: **Swagger UI** и **schema** открыты без ключа.

- **Swagger UI:** `/api/docs/`
- **OpenAPI schema:** `/api/schema/`

---

## Базовые префиксы

| Префикс | Приложение | Описание |
|---------|------------|----------|
| `/api/v1/core/` | core | Теги |
| `/api/v1/events/` | events | События, тематики (аналитика), спикеры, сегменты, галереи, регистрации |
| `/api/v1/news/` | news | Новости (только опубликованные) |
| `/api/v1/content/` | content | Партнёры, команда, настройки сайта, статичные страницы, заявки на партнёрство |
| `/api/v1/materials/` | materials | Категории и материалы |
| `/api/pages/<slug>/` | pages | Страница с блоками (конструктор) по slug |

---

## Эндпоинты по приложениям

Подробное описание полей ответов и параметров запросов — в Swagger (`/api/docs/`) и в документации приложений в папке `app/`.

### Core
- `GET /api/v1/core/tags/` — список тегов
- `GET /api/v1/core/tags/<slug>/` — тег по slug

### Events
- `GET /api/v1/events/themes/`, `GET .../themes/<slug>/` (справочник тематик для внутренней аналитики)
- `GET /api/v1/events/speakers/`, `GET .../speakers/<id>/`
- `GET /api/v1/events/events/` (query: `?status=published&search=...&min_rank=0.12&tag=<slug>&tags=<slug1,slug2>&ordering=-date`), `GET .../events/<slug>/`
- `GET /api/v1/events/segments/`, `GET .../segments/<id>/`
- `GET /api/v1/events/galleries/` (query: `?event=<slug>`), `GET .../galleries/<id>/`
- `GET /api/v1/events/registrations/` — мои регистрации (авторизация)
- `POST /api/v1/events/registrations/` — регистрация на событие (авторизация)

### News
- `GET /api/v1/news/articles/` — список опубликованных статей (query: `?search=...&min_rank=0.12&tag=<slug>&tags=<slug1,slug2>&ordering=-publication_date`)
- `GET /api/v1/news/articles/<slug>/` — статья по slug

### Content
- `GET /api/v1/content/partners/`, `GET .../partners/<id>/`
- `GET /api/v1/content/team/`, `GET .../team/<id>/`
- `GET /api/v1/content/settings/` — настройки сайта (одна запись)
- `GET /api/v1/content/static-pages/`, `GET .../static-pages/<slug>/`
- `POST /api/v1/content/partnership-applications/` — заявка на партнёрство (без авторизации)

### Materials
- `GET /api/v1/materials/categories/`, `GET .../categories/<slug>/`
- `GET /api/v1/materials/materials/` (query: `?search=...&min_rank=0.12&category=<slug>&ordering=-created_at`), `GET .../materials/<id>/`

### Pages (блоки)
- `GET /api/pages/<slug>/` — структура страницы (блоки и элементы) для конструктора фронта

---

## Пагинация и фильтрация

- Списочные эндпоинты используют **PageNumberPagination** (размер страницы задаётся в настройках DRF, по умолчанию 20).
- Для `events/news/materials` включён PostgreSQL **trigram fuzzy search** через параметр `search`:
  - `search` — строка поиска;
  - `min_rank` — порог релевантности (0..1, по умолчанию `0.12`);
  - дополнительные фильтры: `tag/tags` (events/news), `category` (materials).
- Пошаговая инструкция для фронта: `docs/obsidian_pm_meetup/search-swagger-guide.md`.

Подробности — в Swagger и в `config.settings.base` (REST_FRAMEWORK, SPECTACULAR_SETTINGS).
