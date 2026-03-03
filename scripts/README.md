# Скрипты для работы с PM Meetup API

Здесь лежат вспомогательные скрипты для запросов к API (проверка, отладка, выгрузка данных).

## Запуск

- Backend должен быть запущен (`docker compose up` или локально `runserver`).
- Из корня проекта:
  ```bash
  python scripts/fetch_page.py
  python scripts/fetch_page.py about
  ```
- При необходимости задай переменную окружения с API-ключом:
  ```bash
  set API_KEY=твой_токен_из_админки
  python scripts/fetch_page.py home
  ```
  В Linux/macOS: `export API_KEY=...` или положи ключ в `.env` и подставь в скрипт.

## API-ключ

Токен берётся из `/admin/` → «API-ключи». Если `API_KEY` не задан, скрипт использует значение по умолчанию (только для локальной разработки).
