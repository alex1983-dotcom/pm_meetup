# Конфигурация проекта

Переменные окружения и файлы настроек Django. Источник значений по умолчанию: [`.env.example`](../.env.example), `config/settings/*.py`.

---

## Переменные `.env`

Скопируйте `.env.example` → `.env` в корне репозитория.

### Обязательно для Docker (dev)

| Переменная | Назначение |
|------------|------------|
| `POSTGRES_PASSWORD` | Пароль при инициализации контейнера `db` |
| `DB_PASSWORD` | Пароль для Django при подключении к `db` |

**`POSTGRES_PASSWORD` и `DB_PASSWORD` должны совпадать.** Иначе PostgreSQL создаётся с одним паролем, Django подключается с другим — контейнер `web` падает с `password authentication failed`.

После смены пароля при уже существующем volume БД может понадобиться `docker compose down -v` (данные БД удалятся).

### Разработка

| Переменная | Назначение |
|------------|------------|
| `DEBUG` | `1` в dev (`docker-compose.yml` передаёт в `web`) |
| `SECRET_KEY` | Секрет Django |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_HOST`, `DB_PORT` | Подключение к PostgreSQL (`DB_HOST=db` в compose) |
| `POSTGRES_DB`, `POSTGRES_USER` | Имя БД и пользователь для образа postgres |

### Продакшен (см. `docker-compose.prod.yml`)

| Переменная | Назначение |
|------------|------------|
| `NGINX_SERVER_NAME` | Домен для nginx (`server_name`) |
| `ALLOWED_HOSTS` | Список хостов Django через запятую |
| `CSRF_TRUSTED_ORIGINS` | Схема + хост для CSRF, через запятую |
| `LOG_DIR` | Каталог логов в контейнере (том `./logs`) |
| `ENABLE_INFO_LOG` | Опционально в `production.py` — расширенные info-логи |

### Опционально

| Переменная | Назначение |
|------------|------------|
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Почта (если настроена отправка) |
| `CORS_ALLOWED_ORIGINS` | В **`base.py`** — список origin через запятую |

**Важно для Docker dev:** сервис `web` использует `DJANGO_SETTINGS_MODULE=config.settings.development`. Файл `development.py` **задаёт CORS жёстко** (`localhost:3000`, `127.0.0.1:3000`). Переменная `CORS_ALLOWED_ORIGINS` в `.env` в этом режиме **не применяется**.

---

## `config/settings/base.py`

| Настройка | Значение |
|-----------|----------|
| `AUTH_USER_MODEL` | `users.User` (вход по email) |
| `SITE_ID` | `1` (django.contrib.sites) |
| БД | PostgreSQL через `python-decouple` и переменные `DB_*` |
| `FIXTURE_DIRS` | `fixtures/` — `loaddata initial_data` |
| `REST_FRAMEWORK` | JSON, пагинация 20, `DocsOrApiKey`, `SessionAuthentication` |
| `SPECTACULAR_SETTINGS` | OpenAPI, схема `X-API-KEY` |
| Редактор | **django-mdeditor** (`MDTextField`), не CKEditor |

Локальные приложения: `core`, `users`, `events`, `news`, `content`, `pages`, `materials`.

---

## `development.py` vs `production.py`

| | development (Docker dev) | production |
|--|------------------------|------------|
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `['*']` | из env |
| CORS | фиксированный список :3000 | из env / nginx |
| Логи | `./logs/django.log`, `drf.log` | ротация, опционально `ENABLE_INFO_LOG` |
| Security HTTPS | нет | флаги в `production.py` |

---

## См. также

- [docker-commands.md](docker-commands.md)
- [auth-sessions.md](auth-sessions.md)
- [nginx-production.md](nginx-production.md)
