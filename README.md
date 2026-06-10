# Test Task — DimaTech

Асинхронное REST API приложение на FastAPI.

## Стек
- FastAPI + Uvicorn
- SQLAlchemy (async) + asyncpg + PostgreSQL
- Pydantic v2 + pydantic-settings
- JWT (PyJWT) + bcrypt (passlib)
- Alembic
- Docker Compose

## Запуск с Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно на `http://localhost:8000`.
Документация Swagger: `http://localhost:8000/docs`.

## Запуск без Docker

### Требования
- Python 3.12+
- PostgreSQL (запущенный на localhost:5432)

### 1. Установка зависимостей

```bash
poetry install
```

### 2. Настройка .env

Скопируйте `.env.example` в `.env` и отредактируйте:

```bash
cp .env.example .env
```

По умолчанию `.env.example` содержит:

```
DATABASE_URL=postgresql+asyncpg://postgres:your-password-here@localhost:5432/test_task
SECRET_KEY=your-secret-key-here
WEBHOOK_SECRET_KEY=your-webhook-secret-here
JWT_EXPIRE_MINUTES=30
```

### 3. Создание БД

```bash
createdb test_task
```

### 4. Запуск

Сначала примените миграции:

```bash
poetry run alembic upgrade head
```

Затем запустите приложение:

```bash
poetry run uvicorn app.main:app --reload
```

### 5. Доступ

- Приложение: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Seed данные

Для тестирования в миграцию `001_initial.py` добавлены предустановленные пользователи:

| Роль  | Email             | Пароль    |
|-------|-------------------|-----------|
| User  | user@test.com     | user123   |
| Admin | admin@test.com    | admin123  |

> **Безопасность:** Если вы используете приложение не в тестовой среде,
> измените или удалите INSERT-команды в миграции `001_initial.py` и создайте
> новых пользователей через API или напрямую в БД.

## Тестирование

### Автоматические тесты

```bash
poetry install --with test
poetry run python -m pytest tests/ -v
```

Тесты покрывают сервисный слой (`AuthService`, `AdminService`, `UserService`) и HTTP роуты (`/auth/*`, `/admin/*`).

> **Важно:** Это демонстрационные тесты. В рамках тестового задания покрыты auth, admin и webhook (сервисы + API).

Тесты используют отдельную БД `test_task_test` — таблицы создаются автоматически
при старте тестовой сессии, каждый тест откатывает свои изменения.

### Ручное тестирование

Все curl-запросы для ручной проверки — в [MANUAL_TESTS.md](MANUAL_TESTS.md).

## Эндпоинты

| Метод | Путь | Доступ | Описание |
|-------|------|--------|---------|
| POST | `/api/v1/auth/login` | Публичный | Авторизация |
| POST | `/api/v1/auth/logout` | Любой авторизованный | Отзыв токена |

| GET | `/api/v1/users/me` | User | Профиль |
| GET | `/api/v1/users/me/accounts` | User | Список счетов |
| GET | `/api/v1/users/me/transactions` | User | Список платежей |
| GET | `/api/v1/admin/users` | Admin | Список пользователей |
| POST | `/api/v1/admin/users` | Admin | Создать пользователя |
| PUT | `/api/v1/admin/users/{id}` | Admin | Обновить пользователя |
| DELETE | `/api/v1/admin/users/{id}` | Admin | Удалить пользователя |
| GET | `/api/v1/admin/users/{id}/accounts` | Admin | Счета пользователя |
| POST | `/api/v1/webhook/payment` | Публичный | Webhook |
