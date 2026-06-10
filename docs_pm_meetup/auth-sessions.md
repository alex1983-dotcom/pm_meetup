# Доступ к API: ключи, origin и сессии

Документ описывает, **как именно** backend разрешает или запрещает запросы. Это три независимых механизма; они не заменяют друг друга.

---

## 1. Доступ к read-only API (`DocsOrApiKey`)

Настройка: `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` → `apps.core.permissions.DocsOrApiKey`.

Запрос к эндпоинту разрешён, если выполняется **хотя бы одно** из условий:

| Условие | Детали |
|---------|--------|
| Swagger / schema | Пути `/api/docs/` и `/api/schema/` открыты без ключа |
| API-ключ | Заголовок `X-API-KEY` или query `?key=...`; ключ активен в таблице `core.ApiKey` |
| Доверенный origin | Заголовок `Origin` или `Referer` содержит `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:8000` или `http://127.0.0.1:8000` |

Если ни одно условие не выполнено — ответ **403**.

Ключ создаётся в админке: раздел «API-ключи» → «Добавить» → скопировать поле «Токен».

---

## 2. Сессия пользователя (`SessionAuthentication`)

Настройка: `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` → `rest_framework.authentication.SessionAuthentication`.

Сессия — cookie `sessionid`, которую Django выдаёт после успешного входа (сейчас это вход в **`/admin/`** по email и паролю).

Сессия нужна там, где API должен знать **конкретного пользователя**, а не только факт «запрос с доверенного фронта»:

| Эндпоинт | Поведение без сессии | Поведение с сессией |
|----------|----------------------|---------------------|
| `GET /api/v1/events/registrations/` | Пустой список | Регистрации текущего пользователя |
| `POST /api/v1/events/registrations/` | Ошибка валидации «Требуется авторизация…» | Создаётся регистрация с `user=request.user` |

**`X-API-KEY` не подставляет пользователя** и не заменяет сессию для этих эндпоинтов.

Публичного REST-эндпоинта входа (`/api/v1/auth/login/` и т.п.) в проекте **нет**. Приложение `users` не подключено к `config/urls.py` как API.

---

## 3. Как создаются пользователи сейчас

| Способ | Где |
|--------|-----|
| `python manage.py createsuperuser` | CLI / Docker `exec` |
| Админка → Пользователи → Добавить | `/admin/` |
| Фикстуры, `seed_data`, Django shell | Разработка / демо-данные |

`UserManager.create_user` в коде есть, но **не вызывается** из публичного API. Роль по умолчанию при создании — `member`.

---

## 4. Поле `is_blocked` vs `is_active`

| Поле | Где используется | Эффект на вход |
|------|------------------|----------------|
| `is_active` | Стандартное поле Django | `False` — войти нельзя |
| `is_blocked` | Поле проекта, видно в админке | **Не проверяется** при входе в текущем коде |

Для реальной блокировки доступа сейчас используйте `is_active=False`. `is_blocked` — метка для админки; проверку при auth можно добавить отдельной задачей.

---

## 5. Что видит публичный API по умолчанию

| Ресурс | Фильтр публикации в queryset |
|--------|------------------------------|
| Новости `GET /api/v1/news/articles/` | Только `is_published=True` |
| Статичные страницы content `GET .../static-pages/` | Только `is_published=True` |
| События `GET /api/v1/events/events/` | **Все статусы** (`draft`, `published`, …) |
| Деталь события `GET .../events/<slug>/` | Любой статус по slug |
| Сегменты, спикеры, галереи | Без фильтра по статусу родительского события |

Для витрины событий фронт должен передавать **`?status=published`**. Без этого параметра в ответ попадут черновики и отменённые события.

---

## 6. Проверка в dev

1. Read-only API с ключом: `curl -H "X-API-KEY: <токен>" http://localhost:8000/api/v1/core/tags/`
2. Read-only API с фронта: запрос из браузера на `localhost:3000` к `localhost:8000` (CORS настроен в `development.py`).
3. Регистрация на событие: войти в `/admin/` → в том же браузере выполнить `POST /api/v1/events/registrations/` в Swagger.

При появлении session-login для SPA с другого порта потребуется настройка **CSRF** (`CSRF_TRUSTED_ORIGINS` в prod, заголовок `X-CSRFToken`).

---

## См. также

- [api-endpoints.md](api-endpoints.md)
- [app/users-app-documentation.md](app/users-app-documentation.md)
- [app/events-app-documentation.md](app/events-app-documentation.md)
- [project_configuration.md](project_configuration.md)
