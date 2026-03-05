# Запросы к PM Meetup API через PowerShell

Этот файл — шпаргалка, как из PowerShell делать запросы к API проекта с защитой по `X-API-KEY`.

## 1. Что нужно заранее

- Запущен backend (`docker compose up` или `docker-compose up`).
- В админке Django создан **API-ключ**:
  - `/admin/` → «API-ключи» → «Добавить».
  - После сохранения скопируй поле **«Токен»** (40 символов) — это и есть ключ.

Далее в примерах будем использовать:

- Базовый URL API: `http://localhost:8000`
- Ключ (пример): `ZsBm7TxYSp8Zs4UlrnDreNXAipkt20qjwCN3Qnx9`

## 2. Важный момент про PowerShell и curl

В Windows PowerShell команда `curl` — это **алиас** для `Invoke-WebRequest`, а не классический `curl.exe`, из-за чего привычный синтаксис `-H "Header: value"` **не работает**.

Рекомендуется:

- либо использовать **`Invoke-WebRequest`** напрямую;
- либо явно вызывать `curl.exe`.

Ниже примеры обоих вариантов.

## 3. Вариант 1 — Invoke-WebRequest (рекомендуемый)

Пример: получить контент страницы `home` (`/api/pages/home/`).

```powershell
$apiUrl = "http://localhost:8000/api/pages/home/"
$apiKey = "ZsBm7TxYSp8Zs4UlrnDreNXAipkt20qjwCN3Qnx9"  # токен из админки

$headers = @{
    "X-API-KEY" = $apiKey
    "Accept"    = "application/json"
}

$response = Invoke-WebRequest -Uri $apiUrl -Headers $headers -Method GET

# Статус и тело ответа
$response.StatusCode
$response.Content
```

### Пояснения

- `-Headers` принимает **хеш-таблицу** (`@{ ... }`), а не строку.
- Заголовок `X-API-KEY` обязателен для доступа к защищённым эндпоинтам.
- `Accept: application/json` подсказывает серверу, что нам нужен JSON.

## 4. Вариант 2 — классический curl.exe

Если хочется использовать привычный синтаксис curl:

```powershell
curl.exe -X GET "http://localhost:8000/api/pages/home/" ^
  -H "Accept: application/json" ^
  -H "X-API-KEY: ZsBm7TxYSp8Zs4UlrnDreNXAipkt20qjwCN3Qnx9"
```

Обрати внимание:

- Используем **`curl.exe`**, а не просто `curl`, чтобы обойти алиас PowerShell.
- В примере для переноса строки в PowerShell используется `^` (можно написать всё и в одну строку).

## 5. Как менять страницу (slug)

Эндпоинт для страниц:  
`GET /api/pages/<slug>/`

Где `slug` — внутренний код страницы в модели `Page.slug` (например: `home`, `about`, `contacts`).

Примеры:

```powershell
$slug = "home"
$apiUrl = "http://localhost:8000/api/pages/$slug/"

$headers = @{
    "X-API-KEY" = $apiKey
    "Accept"    = "application/json"
}

$response = Invoke-WebRequest -Uri $apiUrl -Headers $headers -Method GET
$response.Content
```

## 6. Быстрая проверка, что ключ рабочий

Если ключ неверный или неактивен, сервер вернёт `403` с сообщением о недостаточных правах.

Правильная последовательность проверки:

1. Скопировать токен из `/admin/` → «API-ключи».
2. Вставить его в переменную `$apiKey`.
3. Выполнить пример из раздела 3.
4. Убедиться, что:
   - `StatusCode` = `200`;
   - в `Content` вернулся JSON с полями `slug`, `name`, `blocks`.

