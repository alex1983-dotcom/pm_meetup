# Поиск в Swagger (events, news, materials)

Документ описывает, как фронтенду тестировать и использовать триграммный fuzzy-поиск через Swagger UI.

## 1. Открыть Swagger

1. Запустите проект и миграции.
2. Откройте `http://localhost:8000/api/docs/`.
3. Разверните нужный тег:
   - `events`
   - `news`
   - `materials`

## 2. Какие параметры доступны

### Общие

- `search` — поисковая строка (fuzzy-поиск через PostgreSQL `pg_trgm`).
- Пока передан **`search`**, список сортируется по **релевантности** (`search_rank`), параметр **`ordering` не применяется** (иначе он перебил бы порядок по дате).
- `min_rank` — порог релевантности `0..1`.
  - Рекомендация:
    - `0.08-0.12` — широкий поиск;
    - `0.15-0.22` — более точный;
    - `0.25+` — только очень похожие совпадения.
- `ordering` — сортировка результата.

### Для events

- `status` — фильтр по статусу события.
- `tag` — один тег по slug.
- `tags` — несколько тегов через запятую.

### Для news

- `tag` — один тег по slug.
- `tags` — несколько тегов через запятую.

### Для materials

- `category` — фильтр по slug категории материала.

## 3. Пошагово: как проверить поиск

### События (events)

1. Откройте `GET /api/v1/events/events/`.
2. Нажмите **Try it out**.
3. Заполните:
   - `search = менеджемнт` (пример с опечаткой),
   - `min_rank = 0.12`,
   - `status = published` (по желанию),
   - `tag = sobytiya` (по желанию).
4. Нажмите **Execute**.
5. Проверьте, что в выдаче возвращаются релевантные события.

Пример запроса:

`/api/v1/events/events/?search=менеджемнт&min_rank=0.12&status=published&tag=sobytiya`

### Новости (news)

1. Откройте `GET /api/v1/news/articles/`.
2. Нажмите **Try it out**.
3. Заполните:
   - `search = проджект менеджер`,
   - `min_rank = 0.12`,
   - `tags = trendy,techconference` (по желанию),
   - `ordering = -publication_date`.
4. Нажмите **Execute**.

Пример запроса:

`/api/v1/news/articles/?search=проджект%20менеджер&min_rank=0.12&tags=trendy,techconference&ordering=-publication_date`

### Материалы (materials)

1. Откройте `GET /api/v1/materials/materials/`.
2. Нажмите **Try it out**.
3. Заполните:
   - `search = воркшп` (пример с опечаткой),
   - `min_rank = 0.10`,
   - `category = courses` (по желанию),
   - `ordering = -created_at`.
4. Нажмите **Execute**.

Пример запроса:

`/api/v1/materials/materials/?search=воркшп&min_rank=0.10&category=courses&ordering=-created_at`

## 4. Рекомендации для фронтенда

- Начинайте с `min_rank=0.12`.
- Если пусто:
  - уменьшите до `0.08`;
  - уберите лишние фильтры (`tag`, `category`).
- Если слишком много нерелевантных результатов:
  - поднимите до `0.18-0.22`;
  - добавьте `tag`/`category`.
- Для поиска по нескольким тегам используйте `tags` через запятую.

## 5. Технические примечания

- Поиск работает на PostgreSQL с расширением `pg_trgm`.
- Для ускорения используются trigram GIN-индексы в миграциях.
- До запуска поиска в среде убедитесь, что миграции применены:
  - `python manage.py migrate`
