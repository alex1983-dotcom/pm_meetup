# Руководство по Docker для PM Meetup

В проекте используется **Docker Compose v2** (`docker compose`). Если у вас установлен только старый бинарь, замените команды на `docker-compose` (с дефисом).

---

## Запуск проекта (разработка)

```bash
# Сборка и запуск контейнеров (фоновый режим)
docker compose up -d

# Сборка и запуск с пересборкой образов
docker compose up --build -d

# Запуск в режиме foreground (видеть логи в терминале)
docker compose up
```

Сервисы: **`db`** (PostgreSQL), **`web`** (Django на порту 8000), **`frontend`** (Node на порту 3000).

---

## Остановка контейнеров

```bash
# Остановить контейнеры (данные в volumes сохраняются)
docker compose down

# Остановить и удалить volumes (PostgreSQL будет переинициализирован при следующем up!)
docker compose down -v

# Остановить и удалить volumes и образы проекта
docker compose down -v --rmi local
```

---

## Миграции базы данных

```bash
# Создать файлы миграций после изменений в models.py
docker compose exec web python manage.py makemigrations

# Применить миграции к базе данных
docker compose exec web python manage.py migrate

# Показать статус миграций
docker compose exec web python manage.py showmigrations

# Откат приложения к указанной миграции (пример)
docker compose exec web python manage.py migrate events 0009_previous_migration_name
```

---

## Тестовые данные (`seed_data`)

Одна команда заполняет приложения тестовыми данными (события, новости, блоки главной и т.д.). Подробности — в коде команды `apps/core/management/commands/seed_data.py`.

```bash
docker compose exec web python manage.py seed_data

# Очистить связанные данные и загрузить заново (осторожно!)
docker compose exec web python manage.py seed_data --clear
```

Локально (venv): `python manage.py seed_data`.

---

## Суперпользователь (админка)

Вход в админку по **email** и паролю (`AUTH_USER_MODEL = users.User`, поле `username` не используется).

```bash
# Интерактивно (запросит email, имя, фамилию, пароль)
docker compose exec web python manage.py createsuperuser
```

Непосредственно из shell (без интерактива; учтите `REQUIRED_FIELDS` — нужны имя и фамилия):

```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(email='admin@example.com').exists() or User.objects.create_superuser('admin@example.com','YourPassword',first_name='Admin',last_name='User')"
```

Смена пароля существующего пользователя:

```bash
docker compose exec web python manage.py changepassword <email>
```

---

## Статика и медиа

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Образ `web` при старте уже выполняет `collectstatic` (см. `docker-compose.yml`). Медиа монтируется в `./media`.

---

## Логи и отладка

```bash
docker compose logs
docker compose logs -f
docker compose logs -f web
docker compose logs -f db
docker compose logs --tail=100 web

# Логи Django (если файл настроен и смонтирован ./logs)
docker compose exec web cat logs/django.log
```

---

## Работа с PostgreSQL

База — **PostgreSQL 15** (образ `postgres:15-alpine`). Параметры подключения задаются в `.env` (`DB_*`, `POSTGRES_*`).

```bash
# Интерактивный psql (пользователь и БД из .env, типично postgres / pm_meetup)
docker compose exec db psql -U postgres -d pm_meetup

# Дамп в файл на хосте
docker compose exec -T db pg_dump -U postgres pm_meetup > backup.sql

# Восстановление из файла на хосте
docker compose exec -T db psql -U postgres -d pm_meetup < backup.sql
```

Пароль для `psql` из переменной окружения контейнера можно не вводить при работе из `exec` в той же сети compose; при запросе пароля с хоста используйте `PGPASSWORD` или `-W`.

---

## Фикстуры

Рекомендуемый способ обновить `fixtures/initial_data.json` — команда **`dump_fixtures`** (перечисляет нужные модели):

```bash
docker compose exec web python manage.py dump_fixtures --seed
```

Развернуть данные из репозитория:

```bash
docker compose exec web python manage.py loaddata initial_data
```

Имя фикстуры — `initial_data` (файл `fixtures/initial_data.json`, каталог задан в `FIXTURE_DIRS`).

Ручной пример `dumpdata` (узкий состав приложений):

```bash
docker compose exec web python manage.py dumpdata core.Tag core.ApiKey users.User --indent 2
```

Полный состав см. в `apps/core/management/commands/dump_fixtures.py`.

Очистка всей БД и загрузка фикстур (уничтожает все данные):

```bash
docker compose exec web python manage.py flush --noinput
docker compose exec web python manage.py loaddata initial_data
```

---

## Django Shell и утилиты

```bash
docker compose exec web python manage.py shell
docker compose exec web python manage.py check
docker compose exec web python manage.py test
```

Показать список URL (расширение **django_extensions**):

```bash
docker compose exec web python manage.py show_urls
```

Покрытие тестов через **coverage** (если установлено в окружении):

```bash
docker compose exec web coverage run manage.py test
docker compose exec web coverage report
```

---

## Production

**Полная пошаговая инструкция развёртывания на сервере** (DNS, `.env`, TLS, миграции, смена домена): [`deployment-full.md`](deployment-full.md).

Сервис **`nginx`** собирается из `Dockerfile.nginx.prod`: multi-stage **React** (`npm run build`), конфиг из **`nginx.prod.conf.template`** — при старте подставляется **`NGINX_SERVER_NAME`** (в `.env` / compose; по умолчанию `admin.pmmeetup.pro`). **HTTPS** на `:443`, **HTTP** на `:80` с `/.well-known/acme-challenge/` и редиректом на HTTPS. TLS-файлы: том **`./ssl`** → `/etc/nginx/ssl/` (`fullchain.pem`, `privkey.pem`). ACME webroot: **`./certbot/www`**. SPA, прокси на Django: `/api/`, `/admin/`, `/mdeditor/`, статика **`./staticfiles`** → `/static/`. CRA: `PUBLIC_URL=/react-assets`.

Перед первым `up`: **`bash scripts/init_ssl_selfsigned.sh`** (временный self-signed) или положить свои PEM в `ssl/`. В `.env` задайте **`NGINX_SERVER_NAME`**, **`ALLOWED_HOSTS`**, **`CSRF_TRUSTED_ORIGINS`** (`https://тот-же-домен`) согласованно при смене домена.

После изменений в `frontend/`, `nginx.prod.conf.template` или `docker/nginx-render-config.sh`: `docker compose -f docker-compose.prod.yml up -d --build`.

```bash
bash scripts/init_ssl_selfsigned.sh   # если ещё нет ssl/*.pem
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml logs -f
```

---

## Образы и контейнеры

```bash
docker ps
docker ps -a
docker images
docker container prune
docker image prune
```

---

## Быстрый чек-лист запуска

```bash
cp .env.example .env   # при необходимости; выровнять POSTGRES_PASSWORD и DB_PASSWORD
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Сервис `web` при старте уже выполняет `migrate`, `collectstatic`, `runserver`. Открыть:

| URL | Описание |
|-----|----------|
| http://localhost:8000/admin/ | Админка |
| http://localhost:8000/api/docs/ | Swagger |
| http://localhost:3000/ | Frontend (контейнер frontend) |

---

## Частые проблемы

| Проблема | Решение |
|----------|---------|
| Контейнер `web` в **Restarting** | `docker compose logs web` — часто неверный пароль БД или старый volume с другим паролем; см. `.env`, при смене пароля БД может понадобиться `docker compose down -v` (данные БД удалятся) |
| Миграции не применяются | `docker compose exec web python manage.py migrate` |
| Пустая БД | `loaddata initial_data` или `seed_data` |
| Порты заняты | `docker compose down`, проверить `docker ps` |

---

## Алиасы (опционально)

В Bash/Zsh можно добавить, например: `alias dce='docker compose exec web python manage.py'`.
