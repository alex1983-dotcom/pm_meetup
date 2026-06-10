# REST API — сводка эндпоинтов для фронтенда

Подробнее о доступе (ключ, origin, сессия): [auth-sessions.md](auth-sessions.md).

Все эндпоинты доступны при заголовке **`X-API-KEY`** (активный ключ из админки) или при запросе с доверенного origin (например, frontend на `localhost:3000`). Исключение: **Swagger UI** и **schema** открыты без ключа.

- **Swagger UI:** `/api/docs/`
- **OpenAPI schema:** `/api/schema/`

---

## Базовые префиксы

| Префикс | Приложение | Описание |
|---------|------------|----------|
| `/api/v1/core/` | core | Теги |
| `/api/v1/events/` | events | События, спикеры, сегменты программы, галереи, регистрации |
| `/api/v1/news/` | news | Новости (только опубликованные) |
| `/api/v1/content/` | content | Партнёры, команда, настройки сайта, статичные страницы, заявки на партнёрство |
| `/api/v1/materials/` | materials | Категории и материалы |
| `/api/pages/<slug>/` | pages | Страница с блоками (конструктор) по slug |

---

## Эндпоинты по приложениям

Подробное описание полей — в Swagger (`/api/docs/`) и в `app/*-documentation.md`.

### Core
- `GET /api/v1/core/tags/` — список тегов
- `GET /api/v1/core/tags/<slug>/` — тег по slug

### Events

**Видимость:** список и деталь события **не** ограничены статусом `published` по умолчанию. Для витрины передавайте `?status=published`. Новости и статичные страницы content фильтруются иначе — см. [auth-sessions.md](auth-sessions.md) §5.

- `GET /api/v1/events/speakers/`, `GET .../speakers/<id>/`
- `GET /api/v1/events/events/` (query: `?status=published&search=...&min_rank=0.12&tag=<slug>&tags=<slug1,slug2>&ordering=-date`), `GET .../events/<slug>/`
- `GET /api/v1/events/segments/`, `GET .../segments/<id>/`
- `GET /api/v1/events/galleries/` (query: `?event=<slug>`), `GET .../galleries/<id>/`
- `GET /api/v1/events/registrations/` — регистрации **текущего** пользователя (**сессия**, не только ключ)
- `POST /api/v1/events/registrations/` — регистрация на событие (**сессия**; тело: `event`, опционально `extra_data`)

Публичного login/register API нет. См. [auth-sessions.md](auth-sessions.md).

### News
- `GET /api/v1/news/articles/` — только `is_published=True` (query: `?search=...&min_rank=0.12&tag=<slug>&tags=<slug1,slug2>&ordering=-publication_date`)
- `GET /api/v1/news/articles/<slug>/` — статья по slug

### Content
- `GET /api/v1/content/partners/`, `GET .../partners/<id>/`
- `GET /api/v1/content/team/`, `GET .../team/<id>/`
- `GET /api/v1/content/settings/` — настройки сайта (одна запись)
- `GET /api/v1/content/static-pages/`, `GET .../static-pages/<slug>/` — только опубликованные
- `POST /api/v1/content/partnership-applications/` — заявка на партнёрство (без сессии)

### Materials
- `GET /api/v1/materials/categories/`, `GET .../categories/<slug>/`
- `GET /api/v1/materials/materials/` (query: `?search=...&min_rank=0.12&category=<slug>&ordering=-created_at`), `GET .../materials/<id>/`

### Pages (блоки)
- `GET /api/pages/<slug>/` — структура страницы (блоки и элементы) для конструктора фронта

---

## Пагинация и фильтрация

- Списочные эндпоинты: **PageNumberPagination** (по умолчанию 20 записей на страницу).
- Для `events` / `news` / `materials`: триграммный поиск PostgreSQL (`pg_trgm`):
  - `search` — строка;
  - `min_rank` — порог 0..1 (по умолчанию `0.12`);
  - при активном `search` сортировка идёт по релевантности, **`ordering` не применяется**;
  - дополнительно: `tag` / `tags` (events, news), `category` (materials), `status` (events).
- Пошаговая проверка в Swagger: [search-swagger-guide.md](search-swagger-guide.md).

Настройки DRF: `config/settings/base.py` (`REST_FRAMEWORK`, `SPECTACULAR_SETTINGS`).
