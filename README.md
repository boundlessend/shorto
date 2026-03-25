# Мини-сервис сокращения ссылок

## локальный запуск

### 1. создать и активировать виртуальное окружение

```bash
python -m venv venv
source venv/Scripts/activate
```

### 2. установить зависимости

```bash
pip install -r requirements.txt
```

### 3. запустить приложение

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

### 1. созданием короткую ссылку

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

### 2. переход по короткому коду

**GET** `/{code}`

- если ссылка существует и активна — происходит редирект;
- если ссылка не найдена — `404`;
- если срок жизни истек — `410`;
- если ссылка деактивирована — `410`.

### 3. статистика по ссылке

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

### 4. деактивация ссылки

**DELETE** `/links/{code}`

пример ответа:

```json
{
  "message": "Ссылку деактивировали, всё ок.",
  "code": "my-link",
  "is_active": false
}
```

### 5. список всех ссылок

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