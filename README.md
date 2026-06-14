# GastroReserve

Бэкенд и фронтенд приложения для бронирования столов и предзаказа еды в ресторанах.

## Стек

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 17, Alembic, Pydantic v2
- **Frontend:** Alpine.js, CSS
- **Infra:** Docker Compose, Nginx, MinIO (S3)

## Быстрый старт

```bash
# 1. Скопировать .env
cp .env.example .env

# 2. Поднять всё
make up

# 3. Применить миграции
make migrate

# 4. Открыть
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Тестовые пользователи

| Логин | Пароль | Роль |
|-------|--------|------|
| `admin` | `admin123` | Администратор |
| `smirnov_manager` | `manager123` | Менеджер |
| `Алексей Иванов` | `password123` | Клиент |

## Команды Make

| Команда | Описание |
|---------|----------|
| `make up` | Собрать и запустить все сервисы |
| `make down` | Остановить все сервисы |
| `make restart` | Перезапустить все сервисы |
| `make ps` | Статус контейнеров |
| `make logs` | Логи всех сервисов |
| `make migrate` | Применить миграции Alembic |
| `make migration m="name"` | Создать новую миграцию |
| `make db-dump` | Сохранить дамп БД в `dumps/dump.sql` |
| `make db-reset` | Сбросить БД из `dumps/dump.sql` |
| `make clean` | Остановить и удалить все данные (volumes) |

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| Frontend | `3000` | Веб-интерфейс (Nginx) |
| Backend | `8000` | REST API (FastAPI) |
| DB | `5432` | PostgreSQL |
| MinIO | `9000` / `9001` | S3-хранилище файлов |

## Структура проекта

```
backend/
  src/
    api_routers/   # Эндпоинты API
    models/        # SQLAlchemy модели
    schemas/       # Pydantic схемы
    core/          # Конфиг, безопасность, зависимости
    main.py        # Точка входа FastAPI
  alembic/         # Миграции
frontend/
  index.html       # Основная страница (Alpine.js)
  js/              # Модули (auth, booking, cart, dashboard, rating, toast)
  css/             # Стили
```

## Дампы БД

Для сброса базы данных к рабочему состоянию:

```bash
make db-dump   # сохранить текущее состояние
make db-reset  # восстановить из дампа
```

Дампы хранятся в `dumps/` (добавлено в `.gitignore`).
