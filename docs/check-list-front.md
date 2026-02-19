Инструкция для Frontend-разработчиков (PM_Meetup)

## 1. Требования
Единственное, что нужно установить на компьютер:
*   **Docker Desktop** (https://www.docker.com/products/docker-desktop/)

*(Python и Node.js находятся внутри контейнеров)*

> Весь процесс разработки будет проводится через контейнеризацию Docker

---

## 2. Старт

```bash
# 1. Клонировать репозиторий
git clone <URL_репозитория>
cd pm_meetup

# 2. Запустить всё (Backend + Frontend + DB)
docker-compose up -d

# 3. Создаем файл миграций
docker-compose exec web python manage.py makemigrations

# 3. Применить миграции
docker-compose exec web python manage.py migrate
```

---
## 3. Создание суперпользователя (для админки)

```bash
docker-compose exec web python manage.py createsuperuser
```

Здесь нужно пройти все шаги
- имя пользователя
- почта
- пароль
- повторить пароль

## 4. Проверка работы

| Сервис             | URL                               | Описание                              |
| ------------------ | --------------------------------- | ------------------------------------- |
| **React Frontend** | `http://localhost:3000`           | Ваше приложение                       |
| **Django Admin**   | `http://localhost:8000/admin/`    | Админка (логин/пароль создаётся ниже) |
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

## Установка зависимостей через Docker

### Команда для установки зависимостей

```
# В корне проекта PM_Meetup
docker-compose exec frontend npm install <название-пакета>
```

### После установки

1. **Пакет устанавливается** внутри контейнера `frontend`
2. **`package.json` обновляется** 
3. **Контейнер автоматически перезапускается** и подхватывает новый пакет
4. **Коммитим** изменённый `package.json` в Git
## 9. API и доступы

*   **API доступно только с ключом** (кроме Swagger и админки).
*   **Получить ключ:** Зайти в админку → раздел "API-ключи" → Создать.
*   **Использовать ключ:**
    *   В заголовке: `X-API-KEY: ваш_ключ`
    *   Или в URL: `?key=ваш_ключ`

