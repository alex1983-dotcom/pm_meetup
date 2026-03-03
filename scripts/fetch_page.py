#!/usr/bin/env python3
"""
Запрос к GET /api/pages/<slug>/ с заголовком X-API-KEY.
Запуск из корня проекта: python scripts/fetch_page.py [slug]
"""
import os
import sys
import json

try:
    import requests  # type: ignore[reportMissingModuleSource]
except ImportError:
    print("Нужна библиотека requests: pip install requests")
    sys.exit(1)

from decouple import config

# Базовый URL API и ключ (читаются из .env или переменных окружения)
API_BASE = config("API_BASE", default="http://localhost:8000")
API_KEY = config("API_KEY", default="")


def fetch_page(slug: str) -> dict:
    url = f"{API_BASE}/api/pages/{slug}/"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    slug = (sys.argv[1] if len(sys.argv) > 1 else "home").strip()
    if not API_KEY:
        print("Предупреждение: API_KEY не задан. Задай переменную API_KEY или добавь ключ в скрипт для dev.")
    try:
        data = fetch_page(slug)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code}", file=sys.stderr)
        if e.response.text:
            print(e.response.text[:500], file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
