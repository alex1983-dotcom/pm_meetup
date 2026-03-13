# Схема моделей Django (graph_models)

Пошаговая инструкция по генерации визуальной схемы моделей проекта с помощью **django-extensions** без установки pygraphviz (только DOT-файл, картинку получаем отдельно).

---

## 1. Установка

Установить только **django-extensions** (pygraphviz не нужен):

```bash
pip install django-extensions
```

В проекте зависимость уже есть в `requirements.txt`; при работе в venv:

```bash
pip install -r requirements.txt
```

---

## 2. Настройка Django

Приложение **django_extensions** должно быть в `INSTALLED_APPS`. В проекте уже добавлено в `config/settings/base.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_extensions',
    # ...
]
```

Если по какой-то причине команда `graph_models` не находится, при локальном запуске указывайте настройки явно: `--settings=config.settings.development`.

---

## 3. Генерация DOT-файла

Команда создаёт файл в формате **DOT** (Graphviz). Из него потом можно получить PNG/SVG.

### Локально (venv)

```bash
# Активировать venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Схема одного приложения (например, events)
python manage.py graph_models events -o schema.dot --settings=config.settings.development

# Схема всех приложений проекта
python manage.py graph_models -a -o schema.dot --settings=config.settings.development

# Только свои приложения (без contrib и сторонних)
python manage.py graph_models core users events news content pages materials -o schema.dot --settings=config.settings.development
```

### Через Docker

В Docker настройки уже подставляются из окружения, `--settings` можно не указывать:

```bash
# Один сервис (например, events)
docker compose exec web python manage.py graph_models events -o schema.dot

# Все приложения
docker compose exec web python manage.py graph_models -a -o schema.dot

# Только свои приложения
docker compose exec web python manage.py graph_models core users events news content pages materials -o schema.dot
```

Файл `schema.dot` появится в корне проекта (так как в `docker-compose.yml` смонтирован каталог `.:/app`).

### Параметры команды

| Параметр | Описание |
|----------|----------|
| `-a` | Все приложения из `INSTALLED_APPS` |
| `-o schema.dot` | Имя выходного файла (можно указать путь, например `docs/schema.dot`) |
| `--settings=...` | Модуль настроек (при локальном запуске, если по умолчанию не подхватывается) |

Имена приложений для явного списка: `core`, `users`, `events`, `news`, `content`, `pages`, `materials`.

---

## 4. Получение картинки из DOT

Файл **schema.dot** — это текст. Чтобы получить PNG или SVG:

### Вариант A: Онлайн (без установки)

1. Откройте в браузере:
   - **https://viz-js.com/** или  
   - **https://edotor.net/**
2. Скопируйте **весь** текст из файла `schema.dot`.
3. Вставьте в поле ввода на сайте.
4. Нажмите кнопку визуализации.
5. При необходимости экспортируйте результат в PNG или SVG.

### Вариант B: Graphviz (локально)

Если установлен [Graphviz](https://graphviz.org/download/):

```bash
# PNG
dot -Tpng schema.dot -o schema.png

# SVG (удобно для масштабирования и вставки в документы)
dot -Tsvg schema.dot -o schema.svg
```

Команду `dot` нужно выполнять в каталоге, где лежит `schema.dot`, или указать полный путь к файлу.

---

## 5. Краткая шпаргалка

| Действие | Команда (Docker) |
|----------|------------------|
| Схема одного приложения | `docker compose exec web python manage.py graph_models events -o schema.dot` |
| Схема всех приложений | `docker compose exec web python manage.py graph_models -a -o schema.dot` |
| Схема своих приложений | `docker compose exec web python manage.py graph_models core users events news content pages materials -o schema.dot` |

| Действие | Как сделать |
|----------|-------------|
| Открыть схему как картинку | Скопировать `schema.dot` → вставить на https://viz-js.com/ → экспорт PNG/SVG |
| PNG из DOT локально | `dot -Tpng schema.dot -o schema.png` (нужен установленный Graphviz) |

---

## 6. Возможные проблемы

- **Unknown command: 'graph_models'** — не загружен модуль настроек с `django_extensions` в `INSTALLED_APPS`. При локальном запуске добавьте: `--settings=config.settings.development`.
- **LookupError: No installed app with label '...'** — в команду попали буквальные символы `...`. Используйте `-a` или перечислите приложения через пробел без `...`.
- **Файл schema.dot пустой или не создаётся** — проверьте, что вы в корне проекта и что путь в `-o` доступен для записи (в Docker файл пишется в `/app`, он смонтирован в корень проекта).
