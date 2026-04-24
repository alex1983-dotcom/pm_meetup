# Полное развёртывание PM Meetup (production)

Пошаговая последовательность для сервера с **Ubuntu** (или совместимым Linux), **Docker** и **`docker compose`**. Стек: **PostgreSQL**, **Django (Gunicorn)**, **Nginx** (сборка React внутри образа), TLS на **443**, редирект с **80**.

Корень проекта на сервере дальше обозначен как **`/var/www/pm_meetup`** — путь можно заменить на свой.

---

## 1. Что должно быть заранее

| Требование | Проверка |
|------------|----------|
| VPS/сервер с публичным IP | — |
| DNS: **A** (или **AAAA**) на ваш домен | `dig +short ваш.домен` |
| Доступ по SSH | `ssh user@сервер` |
| Порты **80** и **443** свободны снаружи | файрвол / панель хостинга |

Имя домена без схемы используется в **`NGINX_SERVER_NAME`** и **`ALLOWED_HOSTS`**. Для CSRF нужен полный origin с **`https://`**.

---

## 2. Установка Docker (если ещё нет)

```bash
sudo apt update
sudo apt install -y ca-certificates curl git

sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Выйдите из SSH и зайдите снова, чтобы группа **`docker`** применилась. Либо выполняйте **`docker`** через **`sudo`** до перелогина.

Проверка:

```bash
docker --version
docker compose version
```

---

## 3. Каталог и код

```bash
sudo mkdir -p /var/www/pm_meetup
sudo chown "$USER":"$USER" /var/www/pm_meetup
cd /var/www/pm_meetup
```

### SSH-ключ на сервере и доступ к GitHub

На сервере ключ хранится в **`~/.ssh/`** этого пользователя (не путать с ключами для входа на сам сервер).

**1. Создать ключ** (без пароля на фразу — удобно для CI/сервера; с паролем — безопаснее):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github_pm_meetup -N ""
```

**2. Показать публичный ключ** — его целиком копируете в GitHub:

```bash
cat ~/.ssh/id_ed25519_github_pm_meetup.pub
```

**3. Добавить ключ в GitHub** (выберите один вариант):

| Вариант | Куда в GitHub | Когда использовать |
|---------|----------------|-------------------|
| **Deploy key** | В репозитории: **`https://github.com/ВАШ_ОРГ/pm_meetup/settings/keys`** → **Add deploy key** — вставить содержимое `.pub` | Один сервер, **только этот** репозиторий; для `git clone` / `git pull` достаточно **Read** |
| **SSH key аккаунта** | **`https://github.com/settings/keys`** → **New SSH key** | Один ключ для **всех** репозиториев аккаунта |

Документация GitHub: [Deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys), [добавить SSH-ключ в аккаунт](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

**4. Сообщить SSH, какой ключ использовать для `github.com`:**

```bash
cat >> ~/.ssh/config <<'EOF'

Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github_pm_meetup
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
```

Чтобы не отвечать интерактивно на вопрос про fingerprint (например, из скрипта), один раз:

```bash
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null
chmod 644 ~/.ssh/known_hosts
```

**5. Первый контакт с GitHub** (подтвердить отпечаток хоста, если не делали `ssh-keyscan`):

```bash
ssh -T git@github.com
```

Должно появиться приветствие и вопрос про fingerprint — **`yes`**, затем сообщение вроде *Hi USERNAME! You've successfully authenticated*.

**6. Клонировать репозиторий по SSH** (подставьте **`ВАШ_ОРГ`** и имя репо, если не `pm_meetup`):

```bash
cd /var/www/pm_meetup
git clone git@github.com:ВАШ_ОРГ/pm_meetup.git .
```

Если каталог уже создан пустым — вы уже в нём, команда с **`.`** в конце кладёт файлы прямо в `/var/www/pm_meetup`.

Если при **Deploy key** нужен **push** с сервера — при добавлении ключа включите **Allow write access** (обычно для прод достаточно только чтения и `git pull`).

---

## 4. Файл `.env` в корне репозитория

Создайте **`/var/www/pm_meetup/.env`** (например `nano .env`). Ниже — **минимально полный** пример для **`docker-compose.prod.yml`**. Все пароли и **`SECRET_KEY`** замените на свои (длинные, случайные).

```env
# --- Django ---
DEBUG=0
SECRET_KEY=сгенерируйте-длинную-случайную-строку

# Один и тот же хост (без https://) — nginx + Django
NGINX_SERVER_NAME=admin.pmmeetup.pro
ALLOWED_HOSTS=admin.pmmeetup.pro,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://admin.pmmeetup.pro

LOG_DIR=/app/logs

# --- PostgreSQL (значения DB_* и POSTGRES_* должны совпадать по смыслу) ---
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pm_meetup
DB_USER=pm_meetup
DB_PASSWORD=надёжный-пароль-одинаковый-ниже
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=pm_meetup
POSTGRES_USER=pm_meetup
POSTGRES_PASSWORD=надёжный-пароль-одинаковый-выше
```

Важно:

- **`DB_PASSWORD`** и **`POSTGRES_PASSWORD`** — **одинаковые**, как **`DB_USER`** / **`POSTGRES_USER`** и **`DB_NAME`** / **`POSTGRES_DB`**.
- При смене домена обновите **`NGINX_SERVER_NAME`**, **`ALLOWED_HOSTS`**, **`CSRF_TRUSTED_ORIGINS`** согласованно (см. раздел 10).

Локальный шаблон без секретов: **`.env.example`** в репозитории.

---

## 5. TLS (сертификаты) перед первым запуском

Nginx ожидает в каталоге **`./ssl`** (на хосте, рядом с `docker-compose.prod.yml`):

- **`fullchain.pem`**
- **`privkey.pem`**

### Вариант A: временный self-signed (быстрый старт)

Браузер покажет предупреждение о сертификате — для проверки стенда нормально.

```bash
cd /var/www/pm_meetup
bash scripts/init_ssl_selfsigned.sh
# или с явным доменом (должен совпадать с NGINX_SERVER_NAME):
# bash scripts/init_ssl_selfsigned.sh admin.pmmeetup.pro
```

### Вариант B: Let's Encrypt

Пока контейнер **nginx** слушает **80** и отдаёт **`/.well-known/acme-challenge/`** из **`./certbot/www`**, можно выпустить сертификат webroot’ом. Пример (на сервере, **certbot** установлен в систему):

```bash
cd /var/www/pm_meetup
mkdir -p certbot/www

# Поднимите только то, что нужно для ACME, или весь стек — см. ниже.
docker compose -f docker-compose.prod.yml up -d

sudo certbot certonly --webroot -w /var/www/pm_meetup/certbot/www -d admin.pmmeetup.pro

sudo install -m 644 /etc/letsencrypt/live/admin.pmmeetup.pro/fullchain.pem /var/www/pm_meetup/ssl/fullchain.pem
sudo install -m 600 /etc/letsencrypt/live/admin.pmmeetup.pro/privkey.pem /var/www/pm_meetup/ssl/privkey.pem
sudo chown "$USER":"$USER" /var/www/pm_meetup/ssl/*.pem
```

Дальше при обновлении сертификата повторяйте копирование или настройте **renewal hooks**.

Подробности: **`ssl/README`** в репозитории.

---

## 6. Сборка и запуск контейнеров

```bash
cd /var/www/pm_meetup

docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

Проверка статуса:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

Сервисы: **`db`** (Postgres), **`web`** (Gunicorn), **`nginx`** (фронт + прокси на **web:8000**).

---

## 7. Миграции и статика

```bash
cd /var/www/pm_meetup

docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 8. Суперпользователь и тестовые данные

Вход в админку — по **email** (поле **`username`** у пользователя отключено).

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

По желанию демо-данные:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py seed_data
```

---

## 9. Проверка в браузере

| URL | Назначение |
|-----|------------|
| `https://ВАШ_ДОМЕН/` | React SPA |
| `https://ВАШ_ДОМЕН/admin/` | Django Admin |
| `https://ВАШ_ДОМЕН/api/docs/` | Swagger (если включён маршрут) |

Замените **`ВАШ_ДОМЕН`** на значение **`NGINX_SERVER_NAME`**.

---

## 10. Смена домена позже

1. В **`.env`** обновите (одинаковый хост везде, где нужен):

   - **`NGINX_SERVER_NAME`**
   - **`ALLOWED_HOSTS`** (список через запятую)
   - **`CSRF_TRUSTED_ORIGINS`** (`https://новый-домен` через запятую, если несколько)

2. Выпустите или скопируйте новые **`ssl/fullchain.pem`** и **`ssl/privkey.pem`** для нового имени (или снова **`scripts/init_ssl_selfsigned.sh новый.домен`** для временного).

3. Пересоберите и перезапустите **nginx** (и при необходимости весь стек):

```bash
cd /var/www/pm_meetup
docker compose -f docker-compose.prod.yml up -d --build nginx
# или полностью:
# docker compose -f docker-compose.prod.yml up -d --build
```

---

## 11. Обновление приложения после `git pull`

```bash
cd /var/www/pm_meetup
git pull

docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 12. Остановка и очистка

Остановить без удаления БД:

```bash
cd /var/www/pm_meetup
docker compose -f docker-compose.prod.yml down
```

**Внимание:** с флагом **`-v`** удалятся тома PostgreSQL — данные пропадут.

```bash
docker compose -f docker-compose.prod.yml down -v
```

---

## 13. Файрвол (пример UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## 14. Полезные логи

```bash
cd /var/www/pm_meetup
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f db
```

Файлы Django на хосте (если пишутся в **`/app/logs`**): каталог **`./logs`** рядом с compose.

---

## 15. Ссылки на код и документацию проекта

| Что | Где |
|-----|-----|
| Compose прод | `docker-compose.prod.yml` |
| Nginx (шаблон домена) | `nginx.prod.conf.template`, `docker/nginx-render-config.sh`, `Dockerfile.nginx.prod` |
| Django прод-настройки | `config/settings/production.py` |
| Команды Docker (dev и общее) | `docs_pm_meetup/docker-commands.md` |
| TLS и домен (кратко) | `ssl/README` |

---

## Краткий чек-лист (все команды подряд после установки Docker и клона)

```bash
cd /var/www/pm_meetup
# 1) создать .env вручную (см. раздел 4)
nano .env

# 2) TLS
bash scripts/init_ssl_selfsigned.sh

# 3) запуск
docker compose -f docker-compose.prod.yml up -d --build

# 4) Django
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 5) опционально
# docker compose -f docker-compose.prod.yml exec web python manage.py seed_data
```

После этого откройте **`https://<NGINX_SERVER_NAME>/`** и **`/admin/`**.
