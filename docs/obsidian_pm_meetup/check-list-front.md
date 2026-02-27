Инструкция для Frontend-разработчиков (PM_Meetup)

## 1. Требования
Единственное, что нужно установить на компьютер:
*   **Docker Desktop** (https://www.docker.com/products/docker-desktop/)

*(Python и Node.js находятся внутри контейнеров)*

> Весь процесс разработки будет проводится через контейнеризацию Docker

---

## 2. Старт

**Перед первым запуском:**

1. В корне проекта создать файл **`.env`** (скопировать из `.env.example`). В `.env` обязательно совпадают пароли для БД: **`POSTGRES_PASSWORD`** и **`DB_PASSWORD`** (одно и то же значение). Иначе контейнер backend будет падать при старте.
2. В корне проекта должна быть папка **`static`** (пустая) — иначе backend выведет предупреждение (на работу не влияет).

```bash
# 1. Клонировать репозиторий
git clone <URL_репозитория>
cd pm_meetup

# 2. Создать .env из шаблона (если ещё нет) и проверить, что POSTGRES_PASSWORD = DB_PASSWORD
# 3. Запустить всё (Backend + Frontend + DB)
docker-compose up -d

# 4. Подождать 10–15 секунд, затем проверить, что backend запущен (не перезапускается)
docker-compose ps
# Контейнер web должен быть в статусе "Up". Если "Restarting" — см. раздел "Типичные проблемы при развёртывании" ниже.

# 5. Создать файлы миграций (если ещё не созданы)
docker-compose exec web python manage.py makemigrations

# 6. Применить миграции
docker-compose exec web python manage.py migrate
```

---
## 3. Создание суперпользователя (для админки)

```bash
docker-compose exec web python manage.py createsuperuser
```

Вход в админку — по **email** и паролю (не по отдельному логину). При создании суперпользователя запрашиваются:

- **Email** (обязательно)
- **Имя**
- **Фамилия**
- **Пароль** и повтор пароля (минимум 8 символов, не совпадать с email)

## 4. Проверка работы

| Сервис             | URL                               | Описание                              |
| ------------------ | --------------------------------- | ------------------------------------- |
| **React Frontend** | `http://localhost:3000`           | Ваше приложение                       |
| **Django Admin**   | `http://localhost:8000/admin/`    | Админка (вход по email и паролю из createsuperuser) |
| **Swagger API**    | `http://localhost:8000/api/docs/` | Документация API                      |

---

## 6. Основные команды

| Задача                 | Команда                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| **Остановить проект**  | `docker-compose down`                                              |
| **Перезапустить**      | `docker-compose restart`                                           |
| **Посмотреть логи**    | `docker-compose logs -f`                                           |
| **Логи только фронта** | `docker-compose logs -f frontend`                                  |
| **Логи только бэка**   | `docker-compose logs -f web`                                       |
| **Создать миграции**   | `docker-compose exec web python manage.py makemigrations`          |
| **Применить миграции** | `docker-compose exec web python manage.py migrate`                 |
| **Собрать статику**    | `docker-compose exec web python manage.py collectstatic --noinput` |

---

## 7. Если что-то сломалось

```bash
# 1. Остановить всё
docker-compose down

# 2. Очистить кэш (если были ошибки сборки)
docker-compose build --no-cache

# 3. Запустить заново
docker-compose up -d
```

---

## 8. Типичные проблемы при развёртывании (Backend и API)

Фронт зависит от backend: если контейнер **web** не запущен или постоянно перезапускается, API не отвечает и фронт не сможет с ним работать. Ниже — частые причины и что делать.

### Контейнер web в статусе "Restarting", команды `exec` не выполняются

**Причина:** backend падает при старте (чаще всего при попытке подключиться к БД или применить миграции).

**Что сделать:**

1. Посмотреть логи backend:
   ```bash
   docker-compose logs web --tail=100
   ```
2. По тексту ошибки:
   - **`password authentication failed for user "postgres"`** — не совпадают пароли БД. В `.env` должны быть одинаковые значения: `POSTGRES_PASSWORD=...` и `DB_PASSWORD=...`. После исправления: `docker-compose down -v` (удалит данные БД!), затем `docker-compose up -d`. Через 10–15 сек снова `makemigrations` и `migrate`.
   - **`Dependency on app with no migrations: users`** или **`BadMigrationError ... has no Migration class`** — сломаны или отсутствуют файлы миграций backend. Это чинится на стороне backend (миграции в репозитории). После обновления кода — снова `docker-compose up -d`, затем `migrate`.

### API не отвечает (502, connection refused, CORS)

- Убедиться, что контейнер **web** в статусе **Up**: `docker-compose ps`.
- Если **Restarting** — действовать по пункту выше (логи `web`, пароли БД, миграции).
- Фронт должен ходить на тот же хост/порт, где поднят backend (в dev обычно `http://localhost:8000`). Проверить в настройках фронта (переменные окружения / .env).

### После первого клона или сброса БД

Рекомендуемый порядок:

1. Создать `.env` из `.env.example`, проверить `POSTGRES_PASSWORD` и `DB_PASSWORD`.
2. `docker-compose up -d`.
3. Подождать 10–15 сек, проверить `docker-compose ps` (web — Up).
4. Если web — Up: `makemigrations`, `migrate`, `createsuperuser`.
5. Открыть фронт и API по URL из таблицы «Проверка работы».

Миграции создаёт и применяет backend; фронту достаточно, чтобы backend был запущен и миграции применены.

---

## 9. Установка зависимостей через Docker

### Команда для установки зависимостей

```
# В корне проекта PM_Meetup
docker-compose exec frontend npm install <название-пакета>
```
## В корне проекта создать `.env`

Шаблон  находится в `.env.example`, в корне проекта

### После установки

1. **Пакет устанавливается** внутри контейнера `frontend`
2. **`package.json` обновляется** 
3. **Контейнер автоматически перезапускается** и подхватывает новый пакет
4. **Коммитим** изменённый `package.json` в Git

## 10. API и доступы

*   **API доступно только с ключом** (кроме Swagger и админки).
*   **Получить ключ:** Зайти в админку → раздел "API-ключи" → Создать.
*   **Использовать ключ:**
    *   В заголовке: `X-API-KEY: ваш_ключ`
    *   Или в URL: `?key=ваш_ключ`

