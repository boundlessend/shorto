# Мини-сервис сокращения ссылок

## локальный запуск

### 1. клонировать репозиторий

```bash
git clone git@github.com:boundlessend/shorto.git
cd shorto
```

### 2. создать и активировать виртуальное окружение

macOS / linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

win powershell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. установить зависимости

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. запустить приложение

```bash
uvicorn app.main:app --reload
```

после старта сервис будет тут:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## как запустить тесты

```bash
pytest .
```

---

## API

### 1. создаем короткую ссылку

**POST** `/links`

пример тела запроса:

```json
{
  "original_url": "https://example.com/very/long/path",
  "custom_code": "my-link",
  "expires_in_seconds": 3600
}
```

поля:

- `original_url` — обязательный URL;
- `custom_code` — опциональный кастомный код;
- `expires_in_seconds` — опциональный TTL в секундах.

пример успешного ответа:

```json
{
  "original_url": "https://example.com/very/long/path",
  "code": "my-link",
  "short_url": "http://127.0.0.1:8000/my-link",
  "created_at": "2026-03-25T10:00:00Z",
  "expires_at": "2026-03-25T11:00:00Z",
  "is_active": true
}
```

### 2. переходим по короткому коду

**GET** `/{code}`

- если ссылка существует и активна — происходит редирект;
- если ссылка не найдена — `404`;
- если срок жизни истек — `410`;
- если ссылка деактивирована — `410`.

### 3. получаем статистиек по ссылке

**GET** `/links/{code}`

пример ответа:

```json
{
  "original_url": "https://example.com/very/long/path",
  "code": "my-link",
  "created_at": "2026-03-25T10:00:00Z",
  "expires_at": "2026-03-25T11:00:00Z",
  "clicks": 3,
  "is_active": true,
  "is_deleted": false
}
```

### 4. деактивируем ссылку

**DELETE** `/links/{code}`

пример ответа:

```json
{
  "message": "Ссылку деактивировали, всё ок.",
  "code": "my-link",
  "is_active": false
}
```

### 5. получаем список всех ссылок

**GET** `/links`

возвращает массив всех ссылок с базовой информацией.

---

## формат ошибок

ответ ошибки приходит единообразно:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "type": "url_parsing",
        "loc": ["body", "original_url"],
        "msg": "Input should be a valid URL"
      }
    ]
  }
}
```

примеры кодов ошибок:

- `validation_error`
- `custom_code_already_exists`
- `link_not_found`
- `link_expired`
- `link_inactive`

---
## сценарии ручной проверки 

### 1. создаем ссылку с автогенерацией кода

```bash
curl -X POST "http://127.0.0.1:8000/links" \

  -H "Content-Type: application/json" \

  -d '{

    "original_url": "https://example.com/long/path"

  }'
```

### 2. создаем ссылку с кастомным кодом

```bash
curl -X POST "http://127.0.0.1:8000/links" \

  -H "Content-Type: application/json" \

  -d '{

    "original_url": "https://example.com/custom",

    "custom_code": "my-custom-code"

  }'
```

### 3. создаем ссылку со сроком жизни

```bash
curl -X POST "http://127.0.0.1:8000/links" \

  -H "Content-Type: application/json" \

  -d '{

    "original_url": "https://example.com/temp",

    "expires_in_seconds": 60

  }'
```

### 4. получаем статистику по ссылке

```bash
curl "http://127.0.0.1:8000/links/my-custom-code"
```

### 5. переходим по короткой ссылке

```bash
curl -i "http://127.0.0.1:8000/my-custom-code"
```

### 6. пробуем создать ссылку с занятым `custom_code`

```bash
curl -X POST "http://127.0.0.1:8000/links" \

  -H "Content-Type: application/json" \

  -d '{

    "original_url": "https://example.com/another",

    "custom_code": "my-custom-code"

  }'
```

ожидается `409 Conflict`.

### 7. деактивируем ссылку и чекаем, что редирект больше не работает

```bash
curl -X DELETE "http://127.0.0.1:8000/links/my-custom-code"

curl -i "http://127.0.0.1:8000/my-custom-code"
```

после деактивации ожидается `410 Gone`.

---

## что некст делаем

1. мб постоянное хранилище (`PostgreSQL` / `Redis`).
2. добавляем rate limiting
3. хз, добавить удаление просроченных ссылок фоном 
4. добавить owner/user и авторизацию
5. добавить более гибкий фильтр и пагинацию для списка ссылок
6. Добавить конфигурацию через `.env`
7. Добавить логирование и middleware для request-id
