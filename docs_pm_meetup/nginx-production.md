# Nginx в production (Docker): конфигурация, пути и команды

Подробное описание того, как в проекте PM Meetup поднимается **nginx** в продакшене: где лежат файлы в репозитории и на сервере, как собирается конфиг, TLS, Let’s Encrypt и типовые команды.

Связанные файлы в корне репозитория:

| Файл | Назначение |
|------|------------|
| [`docker-compose.prod.yml`](../docker-compose.prod.yml) | Сервис `nginx`: порты, тома, переменная `NGINX_SERVER_NAME` |
| [`Dockerfile.nginx.prod`](../Dockerfile.nginx.prod) | Образ: сборка React + nginx + шаблон конфига |
| [`nginx.prod.conf.template`](../nginx.prod.conf.template) | Шаблон виртуального хоста (подстановка домена через `envsubst`) |
| [`docker/nginx-render-config.sh`](../docker/nginx-render-config.sh) | Скрипт при старте контейнера: шаблон → рабочий `default.conf` |
| [`scripts/init_ssl_selfsigned.sh`](../scripts/init_ssl_selfsigned.sh) | Временный self-signed сертификат в `./ssl/` до Let’s Encrypt |
| [`.env.example`](../.env.example) | Пример переменных домена для nginx и Django |

Краткая сводка по Docker: [`docker-commands.md`](docker-commands.md) (раздел Production).

---

## 1. Архитектура

В продакшене **отдельный контейнер `nginx`**:

- Слушает **80** и **443** на хосте (`ports: "80:80"`, `"443:443"`).
- Отдаёт **собранный React** (статический SPA из `frontend/build`).
- Проксирует на контейнер **`web`** (Gunicorn/Django): `/api/`, `/admin/`, `/mdeditor/`.
- Раздаёт **статику Django** с тома: `/static/` → `./staticfiles`, `/media/` → `./media`.
- **TLS**: сертификаты читаются из примонтированного каталога **`./ssl`** на хосте → `/etc/nginx/ssl` в контейнере.
- **ACME (Let’s Encrypt)**: каталог **`./certbot/www`** на хосте → `/var/www/certbot` в контейнере; по HTTP на `:80` отдаётся `/.well-known/acme-challenge/` для проверки домена.

Контейнер **`web`** не публикует порт наружу — с ним общаётся только nginx по внутренней сети Docker (`web:8000`).

---

## 2. Где лежит конфиг nginx (важно различать три уровня)

### 2.1. В репозитории (Git) — то, что правишь при изменении логики

| Путь | Описание |
|------|----------|
| **`nginx.prod.conf.template`** | Единственный «исходник» виртуального хоста для прода. Содержит плейсхолдер **`${NGINX_SERVER_NAME}`** для `server_name`. Остальные `$host`, `$request_uri` и т.д. — это уже переменные **nginx**, их не подменяет `envsubst`. |
| **`docker/nginx-render-config.sh`** | Обёртка: подставляет только `NGINX_SERVER_NAME` через `envsubst '${NGINX_SERVER_NAME}'`, чтобы не сломать остальные `$`-переменные nginx. |
| **`Dockerfile.nginx.prod`** | Копирует шаблон в образ как **`/etc/nginx/default.conf.template`**, скрипт — в **`/docker-entrypoint.d/99-pm-meetup-render.sh`**. |

Обычный файл **`nginx.conf`** в корне репозитория относится к **другой** схеме (не к этому Docker-образу прода); рабочий прод — **`nginx.prod.conf.template`** + Dockerfile.

### 2.2. Внутри образа (после `docker build`)

- **`/etc/nginx/default.conf.template`** — копия шаблона из репозитория.
- **`/docker-entrypoint.d/99-pm-meetup-render.sh`** — запускается официальным entrypoint образа `nginx` **до** старта nginx.

### 2.3. Внутри запущенного контейнера `nginx` (фактический конфиг)

После старта контейнера:

| Путь в контейнере | Содержание |
|-------------------|------------|
| **`/etc/nginx/conf.d/default.conf`** | Итоговый конфиг: уже **без** `${NGINX_SERVER_NAME}`, подставлено реальное имя хоста из переменной окружения. |
| **`/etc/nginx/ssl/fullchain.pem`**, **`privkey.pem`** | Смонтированы с хоста (`./ssl`, только чтение). |
| **`/var/www/certbot`** | Смонтирован с хоста `./certbot/www` для ACME. |

Проверить с хоста (из каталога с `docker-compose.prod.yml`):

```bash
docker compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/conf.d/default.conf
```

Проверить синтаксис nginx без перезапуска:

```bash
docker compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## 3. Как при старте получается `default.conf`

1. В **`docker-compose.prod.yml`** для сервиса `nginx` задано окружение:  
   `NGINX_SERVER_NAME=${NGINX_SERVER_NAME:-admin.pmmeetup.pro}`  
   (значение берётся из **`.env`** на сервере, иначе дефолт).

2. При старте контейнера срабатывает **`/docker-entrypoint.d/99-pm-meetup-render.sh`** (`docker/nginx-render-config.sh`):

   ```sh
   export NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-admin.pmmeetup.pro}"
   envsubst '${NGINX_SERVER_NAME}' </etc/nginx/default.conf.template >/etc/nginx/conf.d/default.conf
   ```

3. Nginx читает **`/etc/nginx/conf.d/*.conf`** стандартным образом.

**Итог:** правки в **`nginx.prod.conf.template`** попадают в прод только после **пересборки образа** `nginx` (`docker compose ... build`) и перезапуска контейнера. Смена только **`NGINX_SERVER_NAME` в `.env`** требует **перезапуска** контейнера `nginx`, чтобы entrypoint снова выполнил рендер (проще всего `docker compose ... up -d` или `restart nginx`).

---

## 4. Соответствие `location` и бэкенда

Из шаблона [`nginx.prod.conf.template`](../nginx.prod.conf.template):

| Префикс | Куда |
|---------|------|
| **`/`** (SPA) | `root /usr/share/nginx/html`, `try_files` → `index.html` |
| **`/react-assets/`** | CRA `PUBLIC_URL=/react-assets` — алиас на тот же build |
| **`/static/`** | Файлы Django: том `./staticfiles` → `/app/staticfiles` |
| **`/media/`** | Загрузки: том `./media` → `/app/media` |
| **`/api/`**, **`/admin/`**, **`/mdeditor/`** | `proxy_pass http://web:8000` (`upstream django_upstream`) |
| **`:80`** `/.well-known/acme-challenge/` | `root /var/www/certbot` — для certbot |
| **Остальное на `:80`** | Редирект **301** на `https://$host$request_uri` |

Заголовки прокси: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` — для корректной работы Django за HTTPS.

---

## 5. Переменные окружения и согласованность с Django

В **`.env`** на сервере (рядом с `docker-compose.prod.yml`) должны быть согласованы:

```env
NGINX_SERVER_NAME=example.com
ALLOWED_HOSTS=example.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://example.com
```

- **`NGINX_SERVER_NAME`** — без схемы (`https` не писать): одно основное имя в `server_name` nginx.
- **`ALLOWED_HOSTS`** — Django; через запятую, без пробелов (как принято в Django `ALLOWED_HOSTS`).
- **`CSRF_TRUSTED_ORIGINS`** — полный URL с **`https://`** для этого домена.

После смены домена: обновить `.env`, перезапустить **`web`** и **`nginx`**, при необходимости перевыпустить сертификат (раздел 7).

---

## 6. TLS: каталог `ssl/` на сервере

На **хосте** (не в Git с секретами):

```
/var/www/pm_meetup/ssl/fullchain.pem
/var/www/pm_meetup/ssl/privkey.pem
```

В контейнере они видны как **`/etc/nginx/ssl/`** (том в compose: `./ssl:/etc/nginx/ssl:ro`).

### 6.1. Первый запуск: временный self-signed

Пока нет Let’s Encrypt, чтобы nginx вообще поднялся на 443:

```bash
cd /path/to/pm_meetup
bash scripts/init_ssl_selfsigned.sh
# или с явным доменом:
bash scripts/init_ssl_selfsigned.sh adminpmmeetup.site
```

Скрипт создаёт **`ssl/fullchain.pem`** и **`ssl/privkey.pem`**, если их ещё нет. Браузер будет ругаться на недоверенный сертификат — это ожидаемо.

Пересоздать: удалить оба `.pem` в `ssl/` и снова запустить скрипт.

### 6.2. Проверка, что nginx видит сертификаты

```bash
docker compose -f docker-compose.prod.yml exec nginx ls -la /etc/nginx/ssl/
```

---

## 7. Let’s Encrypt (certbot на хосте, webroot)

Проект уже отдаёт challenge с **:80** из **`./certbot/www`** (в контейнере `/var/www/certbot`).

### 7.1. Установка certbot (на хосте Linux)

```bash
apt update && apt install -y certbot
```

### 7.2. Выпуск сертификата

Домен должен указывать **A-записью** на IP сервера; порт **80** доступен с интернета.

```bash
cd /var/www/pm_meetup

certbot certonly --webroot \
  -w /var/www/pm_meetup/certbot/www \
  -d adminpmmeetup.site \
  --email your@email.com \
  --agree-tos \
  --non-interactive
```

Подставь свой домен из `NGINX_SERVER_NAME` и почту.

### 7.3. Копирование в `ssl/` (именно отсюда читает nginx в Docker)

```bash
cp /etc/letsencrypt/live/adminpmmeetup.site/fullchain.pem /var/www/pm_meetup/ssl/fullchain.pem
cp /etc/letsencrypt/live/adminpmmeetup.site/privkey.pem   /var/www/pm_meetup/ssl/privkey.pem
chmod 644 /var/www/pm_meetup/ssl/fullchain.pem
chmod 600 /var/www/pm_meetup/ssl/privkey.pem
```

### 7.4. Перезагрузка nginx без простоя контейнера

```bash
cd /var/www/pm_meetup
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 7.5. Проверка TLS с сервера

```bash
echo | openssl s_client -connect adminpmmeetup.site:443 -servername adminpmmeetup.site 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

### 7.6. Продление: таймер, `ssl/` и deploy-hook

#### Зачем это вообще

- Пакет **certbot** на Debian/Ubuntu ставит **`certbot.timer`** (systemd): периодически запускается **`certbot renew`**, который продлевает сертификаты в **`/etc/letsencrypt/live/...`** (срок Let’s Encrypt ~90 дней).
- Контейнер **nginx** в Docker читает ключи только из **`./ssl/`** на хосте (том в `docker-compose.prod.yml`). **`certbot renew` сам в этот каталог не копирует** — после продления файлы в `ssl/` остаются старыми, пока их не обновить и не перезагрузить nginx.

**Deploy-hook** — это обычный **bash-скрипт на сервере** в каталоге **`/etc/letsencrypt/renewal-hooks/deploy/`**. Certbot **сам вызывает** все исполняемые скрипты из `deploy/` после **успешного** продления сертификата. В скрипте: скопировать `fullchain.pem` / `privkey.pem` в `/var/www/pm_meetup/ssl/` и выполнить **`nginx -s reload`** в контейнере.

Проверить, что таймер активен:

```bash
systemctl list-timers | grep certbot
```

Ожидаемо что-то вроде: `certbot.timer` → `certbot.service`.

Проверить, что hook-скрипты ещё не настроены (пустой каталог — значит, копирование в `ssl/` при renew **никто не делает**):

```bash
ls -la /etc/letsencrypt/renewal-hooks/deploy/
```

#### Содержимое скрипта (пример для одного домена)

Имя файла на сервере: **`/etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh`**.

- В переменной **`DOMAIN`** укажи тот же хост, что в **`NGINX_SERVER_NAME`** в `.env` (ниже пример `adminpmmeetup.site`).
- **`SSL_DIR`** и **`COMPOSE_DIR`** — путь к проекту на сервере (ниже `/var/www/pm_meetup`).
- Certbot при вызове hook выставляет **`RENEWED_LINEAGE`** (путь к lineage, например `/etc/letsencrypt/live/adminpmmeetup.site`). Скрипт копирует файлы **только** если lineage относится к твоему домену — чтобы при нескольких сертификатах на сервере не перезаписать чужой.

```bash
#!/bin/bash
set -euo pipefail

SSL_DIR="/var/www/pm_meetup/ssl"
COMPOSE_DIR="/var/www/pm_meetup"
DOMAIN="adminpmmeetup.site"

if [[ -z "${RENEWED_LINEAGE:-}" ]]; then
  exit 0
fi

if [[ "$RENEWED_LINEAGE" != *"$DOMAIN"* ]]; then
  exit 0
fi

cp "$RENEWED_LINEAGE/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp "$RENEWED_LINEAGE/privkey.pem"   "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"

cd "$COMPOSE_DIR"
docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload
```

#### Установка скрипта на сервере (одним блоком)

Выполнять под **root** (или через `sudo`). При другом домене или пути — поправь `DOMAIN`, `SSL_DIR`, `COMPOSE_DIR` внутри heredoc.

```bash
sudo tee /etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh <<'EOF'
#!/bin/bash
set -euo pipefail

SSL_DIR="/var/www/pm_meetup/ssl"
COMPOSE_DIR="/var/www/pm_meetup"
DOMAIN="adminpmmeetup.site"

if [[ -z "${RENEWED_LINEAGE:-}" ]]; then
  exit 0
fi

if [[ "$RENEWED_LINEAGE" != *"$DOMAIN"* ]]; then
  exit 0
fi

cp "$RENEWED_LINEAGE/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp "$RENEWED_LINEAGE/privkey.pem"   "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 600 "$SSL_DIR/privkey.pem"

cd "$COMPOSE_DIR"
docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh
```

#### Проверки

**Сухой прогон renew** (staging Let’s Encrypt, реальные файлы в `live/` не меняет; проверяется, что продление и challenge настроены верно):

```bash
sudo certbot renew --dry-run
```

При успехе в конце будет сообщение вроде: `Congratulations, all simulated renewals succeeded`.

**Ручной прогон hook** (имитация «только что продлили этот lineage»): копирование в `ssl/` и перезагрузка nginx в Docker.

```bash
sudo ls -la /etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh

sudo RENEWED_LINEAGE=/etc/letsencrypt/live/adminpmmeetup.site \
  /etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh
```

Ожидаемо в конце строка nginx: **`signal process started`**. Предупреждение Docker Compose про устаревший ключ **`version`** в `docker-compose.prod.yml` на работу не влияет.

После настройки hook **вручную** после каждого `certbot renew` копировать PEM не нужно: при реальном продлении certbot вызовет скрипт сам.

---

## 8. Полный набор команд Docker Compose (production)

Рабочий каталог — корень проекта на сервере, например **`/var/www/pm_meetup`**. Файл: **`docker-compose.prod.yml`**.

### 8.1. Первый подъём

```bash
cd /var/www/pm_meetup
cp .env.example .env
# отредактировать .env: SECRET_KEY, пароли БД, NGINX_SERVER_NAME, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS

bash scripts/init_ssl_selfsigned.sh   # если ещё нет ssl/*.pem

docker compose -f docker-compose.prod.yml up -d --build
```

### 8.2. Миграции и статика Django (после `up`)

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 8.3. Пересборка после изменений фронта / шаблона nginx / Dockerfile

```bash
cd /var/www/pm_meetup
docker compose -f docker-compose.prod.yml build --no-cache nginx
docker compose -f docker-compose.prod.yml up -d
```

Или одной командой:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 8.4. Логи

```bash
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f web
```

### 8.5. Остановка / перезапуск только nginx

```bash
docker compose -f docker-compose.prod.yml stop nginx
docker compose -f docker-compose.prod.yml start nginx

docker compose -f docker-compose.prod.yml restart nginx
```

### 8.6. Проверка, откуда был запущен стек (на сервере)

```bash
docker inspect pm_meetup-nginx-1 -f '{{index .Config.Labels "com.docker.compose.project.working_dir"}}'
```

(имя контейнера может отличаться; список: `docker ps --format '{{.Names}}'`.)

---

## 9. Смена домена (чек-лист)

1. DNS **A** (и при необходимости **AAAA**) на IP сервера.
2. Обновить **`.env`**: `NGINX_SERVER_NAME`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
3. Выпустить **новый** certbot для нового `-d` или добавить `-d` в один сертификат — по политике Let’s Encrypt.
4. Скопировать новые PEM в **`ssl/`**, `nginx -s reload` в контейнере.
5. `docker compose -f docker-compose.prod.yml up -d` (чтобы `nginx` перерисовал `default.conf` с новым `server_name`).
6. Обновить **`DOMAIN`** (и при необходимости `SSL_DIR` / `RENEWED_LINEAGE` в ручном тесте) в **`/etc/letsencrypt/renewal-hooks/deploy/pm-meetup-nginx.sh`** — см. **раздел 7.6**.

---

## 10. Типовые проблемы

| Симптом | Что проверить |
|---------|----------------|
| **502 Bad Gateway** | `docker compose ... logs web` — Gunicorn упал? Контейнер `web` в `docker ps`? |
| **Статика / медиа 404** | Тома `./staticfiles`, `./media` существуют на хосте; `collectstatic` выполнен. |
| **Редирект HTTPS не тот хост** | `NGINX_SERVER_NAME` совпадает с тем, что в браузере; нет лишнего прокси, меняющего `Host`. |
| **Certbot challenge failed** | С интернета открывается `http://ДОМЕН/.well-known/...` на **этот** nginx; порт 80 не занят другим процессом на хосте. |
| **После renew сертификат «старый»** | Нет или не сработал **deploy-hook** в `/etc/letsencrypt/renewal-hooks/deploy/` — см. **раздел 7.6** выше. Вручную: `cp` из `live/ДОМЕН/` в `ssl/`, затем `docker compose ... exec nginx nginx -s reload`. |

---

## 11. Краткая шпаргалка путей

```
Репозиторий (редактирование)
  nginx.prod.conf.template
  docker/nginx-render-config.sh
  Dockerfile.nginx.prod
  docker-compose.prod.yml
  ssl/                    ← на сервере: PEM (не коммитить секреты)
  certbot/www/            ← webroot для ACME

Сервер (вне репозитория, certbot)
  /etc/letsencrypt/live/<домен>/     ← fullchain.pem, privkey.pem (обновляет renew)
  /etc/letsencrypt/renewal-hooks/deploy/*.sh   ← после успешного renew: копия в ssl/ + reload nginx

Контейнер nginx (runtime)
  /etc/nginx/default.conf.template   ← из образа
  /etc/nginx/conf.d/default.conf   ← результат envsubst
  /etc/nginx/ssl/*.pem             ← монтирование с хоста ./ssl
  /var/www/certbot                 ← монтирование с хоста ./certbot/www
  /usr/share/nginx/html            ← собранный React в образе
```

---

**Актуальность:** при изменении `Dockerfile.nginx.prod`, `nginx.prod.conf.template` или `docker-compose.prod.yml` обновляйте этот документ и при необходимости [docker-commands.md](docker-commands.md).
