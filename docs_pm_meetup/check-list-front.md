Инструкция для Frontend-разработчиков (PM_Meetup)

**Постоянные картинки вне API:** [static-assets-without-api.md](static-assets-without-api.md).

**Доступ к API, сессии, видимость событий:** [auth-sessions.md](auth-sessions.md).

Команды ниже — Docker Compose **v2** (`docker compose`). Старый CLI: `docker-compose` (с дефисом).

## 1. Требования

Единственное, что нужно установить на компьютер:

* **Docker Desktop** (https://www.docker.com/products/docker-desktop/)

Python и Node.js находятся внутри контейнеров.

---

## 2. Старт

**Перед первым запуском:**

1. Создать **`.env`** из `.env.example`. Пароли **`POSTGRES_PASSWORD`** и **`DB_PASSWORD`** должны совпадать.
2. Создать пустую папку **`static/`** у корня (в `.gitignore`) — иначе предупреждение `staticfiles.W004`.

Миграции создавать не нужно — файлы уже в репозитории. Контейнер `web` при старте сам выполняет `migrate`; ниже `migrate` указан для явной проверки после проблем.

```bash
git clone <URL_репозитория>
cd pm_meetup

cp .env.example .env
# Проверить POSTGRES_PASSWORD = DB_PASSWORD

docker compose up -d

docker compose ps
# web — Up (не Restarting)

docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 3. Создание суперпользователя

Без суперпользователя нельзя зайти в `/admin/` и создать API-ключ.

```bash
docker compose exec web python manage.py createsuperuser
```

Вход в админку — по **email** и паролю. Запрашиваются email, имя, фамилия, пароль (мин. 8 символов).

---

## 4. Проверка работы

| Сервис | URL | Описание |
|--------|-----|----------|
| React Frontend | `http://localhost:3000` | Приложение |
| Django Admin | `http://localhost:8000/admin/` | Админка |
| Swagger API | `http://localhost:8000/api/docs/` | Документация API |

---

## 5. Логика API для фронта (кратко)

| Тема | Поведение |
|------|-----------|
| Read-only запросы | `X-API-KEY` **или** запрос из браузера с `localhost:3000` (origin) |
| Список событий | Без `?status=published` приходят и черновики — на витрине всегда добавляйте `status=published` |
| Новости | Только опубликованные (`is_published=True`) |
| Регистрация на событие | Нужна **сессия** пользователя; публичного login API нет |
| Подробности | [auth-sessions.md](auth-sessions.md), [api-endpoints.md](api-endpoints.md) |

---

## 6. Основные команды

| Задача | Команда |
|--------|---------|
| Остановить проект | `docker compose down` |
| Перезапустить | `docker compose restart` |
| Логи | `docker compose logs -f` |
| Логи фронта | `docker compose logs -f frontend` |
| Логи бэка | `docker compose logs -f web` |
| Миграции | `docker compose exec web python manage.py migrate` |
| Суперпользователь | `docker compose exec web python manage.py createsuperuser` |
| Статика | `docker compose exec web python manage.py collectstatic --noinput` |

Фронту: `makemigrations` не нужен — после `git pull` достаточно `migrate`.

---

## 7. Если что-то сломалось

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 8. Типичные проблемы

### Контейнер web в Restarting

```bash
docker compose logs web --tail=100
```

- **`password authentication failed`** — выровнять `POSTGRES_PASSWORD` и `DB_PASSWORD`, затем `docker compose down -v` (данные БД удалятся) и снова `up`.
- **Ошибки миграций** — `git pull`, проверить файлы в `apps/*/migrations/`, снова `up` и `migrate`.

### API не отвечает / CORS

- `docker compose ps` — `web` должен быть **Up**.
- Backend в dev: `http://localhost:8000`.

### Windows: порт 8000 не поднимается

Ошибка `forbidden by its access permissions` — порт в зарезервированном диапазоне Hyper-V. См. [docker-commands.md](docker-commands.md) (раздел «Частые проблемы»).

### После первого клона

1. `.env` с совпадающими паролями БД.
2. `docker compose up -d`.
3. `createsuperuser`.
4. Проверить URL из таблицы §4.

---

## 9. Установка npm-пакетов

```bash
docker compose exec frontend npm install <название-пакета>
```

Пакет ставится в контейнер, `package.json` на хосте обновляется. Контейнер **не перезапускается** автоматически — выполните `docker compose restart frontend` или пересоберите стек. Закоммитьте `package.json` / `package-lock.json`.

---

## 10. API и доступы

* Доступ к read-only API: **`X-API-KEY`**, **`?key=`** или запрос с origin **`localhost:3000`** (см. [auth-sessions.md](auth-sessions.md)).
* Swagger и schema — без ключа.
* Ключ: админка → «API-ключи» → создать → скопировать «Токен».
* Регистрации на события — только с **сессией** (вход в `/admin/` в том же браузере для проверки в Swagger).
