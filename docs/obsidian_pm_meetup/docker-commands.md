#  Полное руководство по Docker командам для PM_Meetup (HUB42)

---

## Запуск проекта (Разработка)

```bash
# Сборка и запуск контейнеров (фоновый режим)
docker-compose up -d

# Сборка и запуск с пересборкой образов
docker-compose up --build -d

# Запуск в режиме foreground (видеть логи в терминале)
docker-compose up
```

---

## Остановка контейнеров

```bash
# Остановить контейнеры (сохраняя данные)
docker-compose down

# Остановить и удалить volumes (осторожно!!! база данных очистится!)
docker-compose down -v

# Остановить и удалить всё (volumes + images)
docker-compose down -v --rmi all
```

---

## Миграции базы данных

```bash
# Создать файлы миграций после изменений в models.py
docker-compose exec web python manage.py makemigrations

# Применить миграции к базе данных
docker-compose exec web python manage.py migrate

# Показать статус миграций
docker-compose exec web python manage.py showmigrations

# Откатить последнюю миграцию
docker-compose exec web python manage.py migrate <app_name> 0000_initial
```

---

## Суперпользователь (Админка)

```bash
# Создать суперпользователя (интерактивно)
docker-compose exec web python manage.py createsuperuser

# Создать суперпользователя без вопросов (через env)
docker-compose exec web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

---

## Статика и медиа

```bash
# Собрать статические файлы
docker-compose exec web python manage.py collectstatic --noinput

# Очистить собранную статику
docker-compose exec web python manage.py collectstatic --clear

# Просмотреть медиа-файлы (внутри контейнера)
docker-compose exec web ls -la /app/media
```

---

## Логи и отладка

```bash
# Просмотр логов всех сервисов
docker-compose logs

# Просмотр логов в реальном времени
docker-compose logs -f

# Логи только backend (web)
docker-compose logs -f web

# Логи только базы данных
docker-compose logs -f db

# Логи за последние 100 строк
docker-compose logs --tail=100 web

# Просмотр логов Django (внутри контейнера)
docker-compose exec web cat logs/django.log

# Просмотр логов DRF (внутри контейнера)
docker-compose exec web cat logs/drf.log
```

---

## Работа с базой данных

```bash
# Подключиться к MySQL внутри контейнера
docker-compose exec db mysql -u pm_meetup -pSuperP@ssw0rd pm_meetup

# Дамп базы данных (создать бэкап)
docker-compose exec db mysqldump -u pm_meetup -pSuperP@ssw0rd pm_meetup > backup.sql

# Восстановить базу из дампа
docker-compose exec -T db mysql -u pm_meetup -pSuperP@ssw0rd pm_meetup < backup.sql

# Посмотреть размер базы данных
docker-compose exec db du -sh /var/lib/mysql
```

---

## Фикстуры (Данные)

```bash
# Создать дамп данных (фикстуры)
docker-compose exec web python manage.py dumpdata --indent 2 --output fixtures/initial_data.json

# Создать дамп конкретных приложений (как в HUB42)
docker-compose exec web python manage.py dumpdata pages equipment blog requests social --indent 2 --output fixtures/initial_data.json

# Загрузить фикстуры в базу
docker-compose exec web python manage.py loaddata fixtures/initial_data.json

# Очистить базу и загрузить фикстуры заново
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

---

## Django Shell и утилиты

```bash
# Открыть Django shell внутри контейнера
docker-compose exec web python manage.py shell

# Проверить настройки Django
docker-compose exec web python manage.py check

# Показать все URL проекта
docker-compose exec web python manage.py show_urls

# Запустить тесты
docker-compose exec web python manage.py test

# Запустить тесты с покрытием
docker-compose exec web python manage.py test --coverage
```

---

## Production

```bash
# Запуск production конфигурации
docker-compose -f docker-compose.prod.yml up -d

# Сборка production образов
docker-compose -f docker-compose.prod.yml build

# Перезапуск production без пересборки
docker-compose -f docker-compose.prod.yml restart

# Просмотр логов production
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Управление образами и контейнерами

```bash
# Посмотреть все запущенные контейнеры
docker ps

# Посмотреть все контейнеры (включая остановленные)
docker ps -a

# Посмотреть все образы
docker images

# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Удалить всё (осторожно!)
docker system prune -a
```

---

## Быстрый чек-лист запуска

```bash
# 2. Поднять контейнеры
docker-compose up -d

# Создать файл миграций
docker-compose exec web python manage.py makemigrations

# 3. Применить миграции
docker-compose exec web python manage.py migrate

# 4. Создать админа
docker-compose exec web python manage.py createsuperuser

# 5. Собрать статику
docker-compose exec web python manage.py collectstatic --noinput

# 6. Открыть в браузере
# http://localhost:8000/admin/
# http://localhost:8000/api/docs/
```

---

## 1️⃣3️⃣ Частые проблемы и решения

| Проблема | Решение |
|----------|---------|
| **Контейнер не запускается** | `docker-compose logs web` — смотреть ошибку |
| **Миграции не применяются** | `docker-compose exec web python manage.py migrate --run-syncdb` |
| **База данных пуста** | `docker-compose exec web python manage.py loaddata fixtures/initial_data.json` |
| **Статика не отображается** | `docker-compose exec web python manage.py collectstatic --noinput --clear` |
| **Порты заняты** | `docker-compose down` и проверить `docker ps` |
| **Permission denied на логи** | `sudo chmod -R 777 logs/` |
| **Изменения в коде не видны** | `docker-compose restart web` или `docker-compose up --build` |

---

## 1️⃣4️⃣ Алиасы для удобства (опционально)

Добавить в `~/.bashrc` или `~/.zshrc`:

```bash
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcmigrate='docker-compose exec web python manage.py migrate'
alias dcshell='docker-compose exec web python manage.py shell'
alias dcsuper='docker-compose exec web python manage.py createsuperuser'
alias dcstatic='docker-compose exec web python manage.py collectstatic --noinput'
```

После добавления:
```bash
source ~/.bashrc  # или source ~/.zshrc
```

Теперь можно писать просто:
```bash
dcup
dcmigrate
dcsuper
```

---

## ✅ Итоговая проверка

После всех команд откройте в браузере:

| URL | Что должно быть |
|-----|-----------------|
| `http://localhost:8000/admin/` | Страница входа в админку |
| `http://localhost:8000/api/docs/` | Swagger документация |
| `http://localhost:3000/` | Frontend (если настроен) |
