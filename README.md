# Бэкенд-сервис для лендинга разработчика

Бэкенд-сервис для лендинга разработчика с REST API, AI-интеграцией, email-уведомлениями, rate limiting, логированием и OpenAPI-документацией.

## Возможности

- `POST /api/contact/` для приема обращений из формы
- Валидация полей `name`, `phone`, `email`, `comment`
- Сохранение обращений в PostgreSQL
- AI-анализ комментария с graceful fallback
- Email-уведомление владельцу сайта
- Копия письма пользователю
- `GET /api/health/` для проверки состояния сервиса
- `GET /api/metrics/` для получения агрегированной статистики
- Логирование запросов в файл
- Логирование ошибок в файл
- Ограничение запросов по IP
- Swagger и ReDoc документация

## Стек технологий

- Python `3.11`
- Django `5.2`
- Django REST Framework
- PostgreSQL
- `drf-yasg` для Swagger/OpenAPI
- `python-dotenv` для переменных окружения
- OpenAI Python SDK для AI-интеграции

## Структура проекта

```text
config/
  settings.py
  urls.py
  middleware.py
  exceptions.py

contact/
  models.py
  serializers.py
  views.py
  services.py
  ai_service.py
  email_service.py
  rate_limit.py
  metrics_service.py
  tests.py
```

## Архитектура

Проект построен по простой слоистой схеме:

- `views.py` принимает HTTP-запросы и возвращает HTTP-ответы.
- `serializers.py` валидирует входные данные.
- `services.py` оркестрирует бизнес-логику создания обращения.
- `ai_service.py` выполняет AI-анализ комментария.
- `email_service.py` отправляет уведомления владельцу и пользователю.
- `rate_limit.py` ограничивает частоту запросов по IP.
- `metrics_service.py` считает агрегированную статистику.

## Переменные окружения

Создайте локальный `.env` на основе `.env.example`.

Основные переменные:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000

DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

DEFAULT_FROM_EMAIL=no-reply@example.com
OWNER_EMAIL=owner@example.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
SERVER_EMAIL=no-reply@example.com

CONTACT_RATE_LIMIT_REQUESTS=5
CONTACT_RATE_LIMIT_WINDOW_SECONDS=3600
```

## Установка и запуск

1. Создать и активировать виртуальное окружение.
2. Установить зависимости.
3. Настроить `.env`.
4. Применить миграции.
5. Запустить сервер.

Пример команд для Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API-эндпоинты

### `POST /api/contact/`

Создает новое обращение.

Тело запроса:

```json
{
  "name": "Анна Иванова",
  "phone": "+7 (999) 123-45-67",
  "email": "anna@example.com",
  "comment": "Хочу обсудить backend-проект и AI-интеграцию."
}
```

Успешный ответ:

```json
{
  "message": "Обращение успешно создано.",
  "id": 1,
  "ai_status": "success"
}
```

Ответ при fallback AI:

```json
{
  "message": "Обращение успешно создано.",
  "id": 2,
  "ai_status": "fallback"
}
```

Пример ошибки валидации:

```json
{
  "name": [
    "Имя должно содержать минимум 2 символа."
  ],
  "phone": [
    "Телефон должен содержать минимум 10 цифр."
  ],
  "comment": [
    "Комментарий должен содержать минимум 10 символов."
  ]
}
```

Пример ответа при превышении лимита:

```json
{
  "detail": "Слишком много обращений. Попробуйте позже. Повторите попытку через 3600 сек."
}
```

### `GET /api/health/`

Ответ:

```json
{
  "status": "ok"
}
```

### `GET /api/metrics/`

Пример ответа:

```json
{
  "total_requests": 13,
  "ai_status_breakdown": {
    "pending": 2,
    "fallback": 11
  },
  "category_breakdown": {
    "unclassified": 13
  },
  "sentiment_breakdown": {
    "unknown": 13
  }
}
```

## OpenAPI-документация

- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## AI-интеграция

AI-анализ реализован в `contact/ai_service.py`.

Текущее поведение:

- Если задан `OPENAI_API_KEY`, backend отправляет комментарий в OpenAI.
- Модель должна вернуть:
  - `sentiment`
  - `category`
  - `summary`
- Результат сохраняется в базе.

Поддерживаемые значения:

- Тональность:
  - `positive`
  - `neutral`
  - `negative`
- Категория:
  - `project`
  - `consultation`
  - `partnership`
  - `job`
  - `other`

### Graceful fallback

Если AI недоступен, обращение все равно сохраняется и обрабатывается дальше.

Fallback-значения:

- `ai_status = fallback`
- `sentiment = unknown`
- `category = unclassified`
- `ai_error` содержит причину сбоя

## Email-уведомления

Логика email реализована в `contact/email_service.py`.

После создания обращения:

- одно письмо отправляется владельцу сайта
- одно письмо отправляется пользователю как подтверждение

Во время локальной разработки можно использовать `console` email backend.

Для реального SMTP-тестирования с Yandex:

- в проекте рабочей оказалась конфигурация `587 + TLS`
- если отправка зависает при включенном VPN, отключите VPN и повторите тест

## Логирование

Логи сохраняются в:

- `logs/requests.log`
- `logs/errors.log`

### `requests.log`

Содержит:

- HTTP-метод
- путь
- статус-код
- IP-адрес
- длительность запроса
- тело запроса

### `errors.log`

Содержит:

- обработанные API-исключения
- необработанные API-исключения
- ошибки отправки email

## Ограничение запросов

Rate limiting реализован в `contact/rate_limit.py`.

- лимит применяется по IP
- хранение реализовано через file-based cache Django
- конфигурация по умолчанию:
  - `5` запросов
  - за `3600` секунд

При превышении лимита API возвращает `429 Too Many Requests`.

## Тесты

Реализованы тесты для:

- health-check endpoint
- успешного создания обращения
- ошибок валидации
- rate limiting
- metrics endpoint

Запуск тестов:

```powershell
python manage.py test contact
```

## Что было сделано с помощью AI

AI использовался как вспомогательный инженерный инструмент в процессе разработки:
- для ускорения проектирования структуры API и сервисного слоя
- для генерации черновых вариантов отдельных участков кода
- для проверки идей по graceful fallback, rate limiting и обработке ошибок
- для подготовки черновиков документации и тестовых сценариев

Итоговая реализация, структура проекта, отладка, интеграция компонентов и доработка кода выполнялись вручную.

## Примечания

- Без `OPENAI_API_KEY` API продолжает работать через fallback.
- Поведение SMTP может зависеть от локальной сети и VPN.
