# Карта кодовой базы PM Meetup

Краткий ориентир по репозиторию. Детали моделей и API — в `docs/app/*` и в Swagger `/api/docs/`.

## Корень проекта

| Путь | Назначение |
|------|------------|
| `config/` | Настройки Django: `settings` (base, development, production), `urls.py`, `wsgi.py` |
| `apps/` | Пакеты приложений (`apps.<name>`) |
| `fixtures/` | JSON-фикстуры (`initial_data.json`), см. `fixtures/README.md` |
| `frontend/` | React (CRA), см. `frontend/README.md` |
| `scripts/` | Вспомогательные скрипты |
| `manage.py` | Точка входа Django |
| `docker-compose.yml` | Локальная разработка: сервисы `db` (PostgreSQL 15), `web` (Django), `frontend` (Node) |
| `docker-compose.prod.yml` | Production-сборка |
| `requirements.txt` | Зависимости Python |

Каталоги **`media/`**, **`logs/`**, **`staticfiles/`** создаются при работе приложения; часть из них в `.gitignore`. Для устранения предупреждения `staticfiles.W004` в разработке может потребоваться локально создать пустой каталог **`static/`** у корня (он в `.gitignore`).

## Приложения (`apps/`)

| Приложение | Назначение |
|------------|------------|
| **core** | Общие модели (`Tag`, `ApiKey`), `TimeStampedModel`, команды `seed_data`, `dump_fixtures` |
| **users** | Пользователь: `AUTH_USER_MODEL = users.User`, вход по **email** (поле `username` отключено) |
| **events** | События, спикеры, сегменты программы, регистрации, галереи |
| **news** | Новости |
| **content** | Партнёры, команда, singleton-настройки сайта, статические страницы (Markdown), заявки на партнёрство |
| **pages** | Конструктор страниц из блоков для SPA: `Page`, `BlockType`, `PageBlock`, `BlockItem`; API `GET /api/pages/<slug>/` |
| **materials** | Категории материалов и сами материалы |

Важно: есть **две** независимые модели «страница»:

- **`content.Page`** — текстовые страницы (О нас, контакты) с полем `content` (MDEditor).
- **`pages.Page`** — логическая страница конструктора (например `home`) с привязанными блоками.

## API

- Префикс REST: `/api/v1/...`, страницы с блоками: `/api/pages/<slug>/`.
- Документация OpenAPI: `/api/schema/`, Swagger UI: `/api/docs/`.
- Сводка маршрутов: `docs/api-endpoints.md`.
